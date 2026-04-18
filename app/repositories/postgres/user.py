import uuid
from typing import Sequence

from models.user import User, UserUpdate
from models.user_profile import UserProfile
from pydantic import EmailStr
from repositories.user import UserRepository
from sqlmodel import Session, col, func, select


class PostgresUserRepository(UserRepository):
    def __init__(
        self,
        engine,
    ) -> None:
        self.engine = engine

    def get_users(self, offset: int, limit: int) -> tuple[Sequence[User], int]:
        with Session(self.engine) as session:
            count_statement = select(func.count()).select_from(User)
            count = session.exec(count_statement).one()

            statement = (
                select(User)
                .order_by(col(User.created_at).desc())
                .offset(offset)
                .limit(limit)
            )

            users = session.exec(statement).all()

            return users, count

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        with Session(self.engine) as session:
            return session.get(User, user_id)

    def get_by_email(self, user_email: EmailStr) -> User | None:
        with Session(self.engine) as session:
            statement = select(User).where(User.email == user_email)
            user = session.exec(statement).first()

            return user

    def add_user(self, user_in: User) -> User:
        with Session(self.engine) as session:
            session.add(user_in)
            session.flush()

            profile = UserProfile(user_id=user_in.id)
            session.add(profile)

            session.commit()
            session.refresh(user_in)

            return user_in

    def update_user(self, user_db: User, user_in: UserUpdate) -> User:
        with Session(self.engine) as session:
            update_data = user_in.model_dump(
                exclude_unset=True,
            )

            user_db.sqlmodel_update(update_data)
            session.add(user_db)
            session.commit()
            session.refresh(user_db)

            return user_db
