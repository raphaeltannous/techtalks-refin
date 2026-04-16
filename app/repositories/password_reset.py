from abc import ABCMeta, abstractmethod

from models.password_reset import PasswordReset, PasswordResetUpdate


class PasswordResetRepository:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_by_hash(self, hash: str) -> PasswordReset | None:
        pass

    @abstractmethod
    def add(self, password_reset_in: PasswordReset) -> PasswordReset:
        pass

    @abstractmethod
    def update(
        self, password_reset_db: PasswordReset, password_reset_in: PasswordResetUpdate
    ) -> PasswordReset:
        pass
