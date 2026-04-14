import uuid
from datetime import timedelta

from fastapi import BackgroundTasks

import security.jwt_token
import security.password_hashing
from config import settings
from mail.mailer import Mailer
from mail.template_manager import EmailTemplateManager
from models.jwt import Token
from models.user import User, UserPublic, UserRegister, UsersPublic, UserUpdate
from pydantic import EmailStr
from repositories.user import UserRepository


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        mail_template_manager: EmailTemplateManager,
        mailer: Mailer,
    ) -> None:
        self.user_repository = user_repository
        self.mail_template_manager = mail_template_manager
        self.mailer = mailer

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
    ) -> Token | None:
        user = self.get_by_email(email)

        # Timing attack prevention
        if not user:
            security.password_hashing.verify_password(
                password,
                settings.DUMMY_PASSWORD_HASH,
            )

            return None

        verified, updated_password_hash = security.password_hashing.verify_password(
            password,
            user.hashed_password,
        )

        if not verified:
            return None

        # TODO: Send it back to the handler to catch it.
        # How should I send it to the handler?
        # Using errors or is there another way?
        if not user.is_active:
            return None

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
                user.id,
                expires_delta=access_token_expires,
            )
        )

    def register(
        self,
        *,
        user_in: UserRegister,
        background_tasks: BackgroundTasks,
    ) -> UserPublic | None:
        user_db = self.get_by_email(user_in.email)
        if user_db:
            return None  # TODO: Raise error

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
            )
        )

        return UserPublic.model_validate(user)
