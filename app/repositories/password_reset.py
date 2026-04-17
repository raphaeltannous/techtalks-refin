import uuid
from abc import ABCMeta, abstractmethod

from models.password_reset import PasswordReset, PasswordResetUpdate


class PasswordResetRepository:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_by_user_id(self, user_id: uuid.UUID) -> PasswordReset | None:
        pass

    @abstractmethod
    def get_by_token_hash(self, token_hash: str) -> PasswordReset | None:
        pass

    @abstractmethod
    def add(self, password_reset_in: PasswordReset) -> PasswordReset:
        pass

    @abstractmethod
    def update(
        self,
        db_obj: PasswordReset,
        obj_in: PasswordResetUpdate,
    ) -> PasswordReset:
        pass
