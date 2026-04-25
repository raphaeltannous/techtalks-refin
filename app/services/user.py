import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import security.jwt_token
import security.password_hashing
from blake3 import blake3
from config import settings
from exceptions import (
    DuplicateUserError,
    InactiveUserError,
    IncorrectCredentialsError,
    InvalidEmailVerificationToken,
    InvalidPasswordResetToken,
    UserNotFoundError,
)
from fastapi import BackgroundTasks
from mail.mailer import Mailer
from mail.template_manager import EmailTemplateManager
from models.email_verification import EmailVerification, EmailVerificationUpdate
from models.jwt import Token
from models.password_reset import (
    PasswordReset,
    PasswordResetRequest,
    PasswordResetRequestUpdate,
    PasswordResetUpdate,
)
from models.user import User, UserPublic, UserRegister, UsersPublic, UserUpdate
from pydantic import EmailStr
from repositories.email_verification import EmailVerificationRepository
from repositories.password_reset import PasswordResetRepository
from repositories.user import UserRepository


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_reset_repository: PasswordResetRepository,
        email_verification_repository: EmailVerificationRepository,
        mail_template_manager: EmailTemplateManager,
        mailer: Mailer,
    ) -> None:
        self.user_repository = user_repository
        self.password_reset_repository = password_reset_repository
        self.email_verification_repository = email_verification_repository
        self.mail_template_manager = mail_template_manager
        self.mailer = mailer

        self.logger = logging.getLogger("uvicorn.error")

    def get_public_users(self, offset: int, limit: int) -> UsersPublic:
        users, count = self.user_repository.get_users(offset, limit)

        users_public = [UserPublic.model_validate(user) for user in users]

        return UsersPublic(users=users_public, count=count)

    def get_private_users(self, offset: int, limit: int) -> tuple[list[User], int]:
        users, count = self.user_repository.get_users(offset, limit)

        users = [u for u in users]

        return users, count

    def get_by_id(self, id: uuid.UUID) -> User | None:
        return self.user_repository.get_by_id(id)

    def get_by_email(self, email: EmailStr) -> User | None:
        return self.user_repository.get_by_email(email)

    def authenticate(
        self,
        *,
        email: EmailStr,
        password: str,
    ) -> Token:
        user = self.get_by_email(email)

        # Timing attack prevention
        if not user:
            security.password_hashing.verify_password(
                password,
                settings.DUMMY_PASSWORD_HASH,
            )

            raise IncorrectCredentialsError()

        verified, updated_password_hash = security.password_hashing.verify_password(
            password,
            user.hashed_password,
        )

        if not verified:
            raise IncorrectCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        if updated_password_hash:
            user_in = UserUpdate(
                hashed_password=updated_password_hash,
            )

            self.user_repository.update_user(
                user,
                user_in,
            )

        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        return Token(
            access_token=security.jwt_token.create_access_token(
                user.username,
                expires_delta=access_token_expires,
            )
        )

    def register(
        self,
        *,
        user_in: UserRegister,
        background_tasks: BackgroundTasks,
    ) -> UserPublic:
        user_db = self.get_by_email(user_in.email)
        if user_db:
            raise DuplicateUserError()

        user_db = self.__get_by_username(user_in.username)
        if user_db:
            raise DuplicateUserError()

        user = User.model_validate(
            user_in,
            update={
                "hashed_password": security.password_hashing.get_password_hash(
                    user_in.password,
                ),
            },
        )

        user = self.user_repository.add_user(
            user,
        )

        background_tasks.add_task(
            self.mailer.send_html_email,
            self.mail_template_manager.welcome_email(
                user=user,
            ),
        )

        background_tasks.add_task(
            self.send_verification_email,
            user=user,
        )

        return UserPublic.model_validate(user)

    def password_reset_request(
        self,
        *,
        password_reset_request: PasswordResetRequest,
        background_tasks: BackgroundTasks,
    ) -> None:
        user = self.get_by_email(
            email=password_reset_request.email,
        )

        if not user:
            return None

        token = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
        )
        token_hash = blake3(token.encode("utf-8")).hexdigest()

        password_reset = self.password_reset_repository.get_by_user_id(
            user_id=user.id,
        )

        if password_reset:
            self.password_reset_repository.update(
                password_reset,
                PasswordResetUpdate(
                    token_hash=token_hash,
                    expires_at=expires_at,
                ),
            )
        else:
            password_reset = self.password_reset_repository.add(
                PasswordReset(
                    user_id=user.id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                )
            )

        background_tasks.add_task(
            self.mailer.send_html_email,
            self.mail_template_manager.password_reset_email(
                user=user,
                reset_link=urljoin(
                    settings.FRONTEND_PASSWORD_RESET_URL + "/",
                    token,
                ),
                expiration_minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
            ),
        )

    def password_reset_request_update(
        self,
        *,
        prru_in: PasswordResetRequestUpdate,
        background_tasks: BackgroundTasks,
    ) -> None:
        token_hash = blake3(prru_in.token.encode("utf-8")).hexdigest()

        pr_db_obj = self.password_reset_repository.get_by_token_hash(
            token_hash=token_hash,
        )

        if not pr_db_obj:
            raise InvalidPasswordResetToken()

        current_date = datetime.now(timezone.utc)

        if current_date >= pr_db_obj.expires_at:
            raise InvalidPasswordResetToken()

        # Valid token
        password_hash = security.password_hashing.get_password_hash(
            prru_in.password,
        )
        db_user = self.get_by_id(
            pr_db_obj.user_id,
        )

        if not db_user:
            self.logger.error("User does not exist for a valid token")
            raise InvalidPasswordResetToken()

        user_in = UserUpdate(
            hashed_password=password_hash,
        )

        db_user = self.user_repository.update_user(
            db_user,
            user_in,
        )

        self.password_reset_repository.update(
            db_obj=pr_db_obj,
            obj_in=PasswordResetUpdate(
                expires_at=datetime.now(timezone.utc),
            ),
        )

        background_tasks.add_task(
            self.mailer.send_html_email,
            self.mail_template_manager.password_updated(
                user=db_user,
            ),
        )

    def send_verification_email(
        self,
        *,
        user: User,
    ) -> None:
        token = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
        )
        token_hash = blake3(token.encode("utf-8")).hexdigest()

        email_verification = self.email_verification_repository.get_by_user_id(
            user_id=user.id,
        )

        if email_verification:
            self.email_verification_repository.update(
                email_verification,
                EmailVerificationUpdate(
                    token_hash=token_hash,
                    expires_at=expires_at,
                ),
            )
        else:
            self.email_verification_repository.add(
                EmailVerification(
                    user_id=user.id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                )
            )

        self.mailer.send_html_email(
            self.mail_template_manager.email_verification_email(
                user=user,
                verification_link=urljoin(
                    settings.FRONTEND_EMAIL_VERIFICATION_URL + "/",
                    token,
                ),
                expiration_minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
            ),
        )

    def email_verification_request(
        self,
        *,
        current_user: User,
        background_tasks: BackgroundTasks,
    ) -> None:
        if current_user.is_verified:
            return None

        background_tasks.add_task(
            self.send_verification_email,
            user=current_user,
        )

    def email_verification_confirm(
        self,
        *,
        token: str,
    ) -> None:
        token_hash = blake3(token.encode("utf-8")).hexdigest()

        ev_db_obj = self.email_verification_repository.get_by_token_hash(
            token_hash=token_hash,
        )

        if not ev_db_obj:
            raise InvalidEmailVerificationToken()

        current_date = datetime.now(timezone.utc)

        if current_date >= ev_db_obj.expires_at:
            raise InvalidEmailVerificationToken()

        # Valid token
        db_user = self.get_by_id(ev_db_obj.user_id)

        if not db_user:
            self.logger.error(
                "User does not exist for a valid email verification token"
            )
            raise InvalidEmailVerificationToken()

        self.user_repository.update_user(
            db_user,
            UserUpdate(is_verified=True),
        )

        # Invalidate the token immediately by expiring it
        self.email_verification_repository.update(
            db_obj=ev_db_obj,
            obj_in=EmailVerificationUpdate(
                expires_at=datetime.now(timezone.utc),
            ),
        )

    def __get_by_username(self, username: str) -> User:
        user = self.user_repository.get_by_username(username)
        if not user:
            raise UserNotFoundError()

        return user
