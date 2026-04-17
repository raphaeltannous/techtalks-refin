from abc import ABCMeta, abstractmethod

from models.email_verification import EmailVerification, EmailVerificationUpdate


class EmailVerificationRepository:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_by_token_hash(self, token_hash: str) -> EmailVerification | None:
        pass

    @abstractmethod
    def add(self, email_verification_in: EmailVerification) -> EmailVerification:
        pass

    @abstractmethod
    def update(
        self,
        db_obj: EmailVerification,
        obj_in: EmailVerificationUpdate,
    ) -> EmailVerification:
        pass
