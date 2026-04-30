import uuid
from abc import ABCMeta, abstractmethod
from typing import Sequence

from models.user_experience import UserExperience, UserExperienceUpdate


class UserExperienceRepository:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_all_by_user_profile_id(
        self,
        user_profile_id: uuid.UUID,
    ) -> Sequence[UserExperience]:
        pass

    @abstractmethod
    def get_by_id(
        self,
       experience_id: uuid.UUID,
    ) -> UserExperience | None:
        pass

    @abstractmethod
    def add(
        self,
       experience_in: UserExperience,
    ) -> UserExperience:
        pass

    @abstractmethod
    def update(
        self,
       experience_db: UserExperience,
       experience_in: UserExperienceUpdate,
    ) -> UserExperience:
        pass

    @abstractmethod
    def delete(
        self,
       experience_db: UserExperience,
    ) -> None:
        pass
