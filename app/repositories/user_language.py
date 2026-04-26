import uuid
from abc import ABCMeta, abstractmethod
from typing import Sequence

from models.user_language import UserLanguage, UserLanguageUpdate


class UserLanguageRepository:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_all_by_user_profile_id(
        self,
        user_profile_id: uuid.UUID,
    ) -> Sequence[UserLanguage]:
        pass

    @abstractmethod
    def get_by_id(
        self,
        language_id: uuid.UUID,
    ) -> UserLanguage | None:
        pass

    @abstractmethod
    def add(
        self,
        language_in: UserLanguage,
    ) -> UserLanguage:
        pass

    @abstractmethod
    def update(
        self,
        language_db: UserLanguage,
        language_in: UserLanguageUpdate,
    ) -> UserLanguage:
        pass

    @abstractmethod
    def delete(
        self,
        language_db: UserLanguage,
    ) -> None:
        pass
