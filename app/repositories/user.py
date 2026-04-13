import uuid
from abc import ABCMeta, abstractmethod
from typing import Sequence

from models.user import User, UserUpdate
from pydantic import EmailStr


class UserRepository:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_users(self, offset: int, limit: int) -> tuple[Sequence[User], int]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        pass

    @abstractmethod
    def get_by_email(self, user_email: EmailStr) -> User | None:
        pass

    @abstractmethod
    def add_user(self, user_in: User) -> User:
        pass

    @abstractmethod
    def update_user(self, user_db: User, user_in: UserUpdate) -> User | None:
        pass
