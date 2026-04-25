import uuid
from abc import ABCMeta, abstractmethod
from typing import Sequence

from models.user_skill import UserSkill, UserSkillUpdate


class UserSkillRepository:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_all_by_user_profile_id(
        self,
        user_profile_id: uuid.UUID,
    ) -> Sequence[UserSkill]:
        pass

    @abstractmethod
    def get_by_id(
        self,
        skill_id: uuid.UUID,
    ) -> UserSkill | None:
        pass

    @abstractmethod
    def add(
        self,
        skill_in: UserSkill,
    ) -> UserSkill:
        pass

    @abstractmethod
    def update(
        self,
        skill_db: UserSkill,
        skill_in: UserSkillUpdate,
    ) -> UserSkill:
        pass

    @abstractmethod
    def delete(
        self,
        skill_db: UserSkill,
    ) -> None:
        pass
