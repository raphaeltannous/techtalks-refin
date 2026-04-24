import logging
import uuid

from exceptions import (
    ForbiddenAction,
    UserNotFoundError,
    UserProfileNotFoundError,
    UserSkillNotFoundError,
)
from models.user import User
from models.user_profile import UserProfile
from models.user_skill import (
    UserSkill,
    UserSkillIn,
    UserSkillPublic,
    UserSkillsPublic,
    UserSkillUpdate,
)
from repositories.user import UserRepository
from repositories.user_profile import UserProfileRepository
from repositories.user_skill import UserSkillRepository


class UserProfileService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_skill_repository: UserSkillRepository,
        user_profile_repository: UserProfileRepository,
    ) -> None:
        self.user_repository = user_repository
        self.user_skill_repository = user_skill_repository
        self.user_profile_repository = user_profile_repository

        self.logger = logging.getLogger("uvicorn.error")

    def get_by_user_id(
        self,
        *,
        user_id: uuid.UUID,
    ) -> UserProfile | None:
        return self.user_profile_repository.get_by_user_id(
            user_id,
        )

    def get_all_skills_by_username(
        self,
        *,
        username: str,
    ) -> UserSkillsPublic:
        user = self.__get_user_by_username(
            username=username,
        )

        user_profile = self.__get_user_profile_by_user_id(
            user_id=user.id,
        )

        skills = self.user_skill_repository.get_all_by_user_profile_id(
            user_profile.id,
        )

        public_skills = [UserSkillPublic.model_validate(s) for s in skills]

        return UserSkillsPublic(
            skills=public_skills,
        )

    def add_skill(
        self,
        *,
        user_profile: UserProfile,
        skill_in: UserSkillIn,
    ) -> UserSkillPublic:
        skill = UserSkill.model_validate(
            skill_in,
            update={
                "user_profile_id": user_profile.id,
            },
        )

        skill = self.user_skill_repository.add(
            skill,
        )

        return UserSkillPublic.model_validate(
            skill,
        )

    def get_skill_by_id(
        self,
        *,
        skill_id: uuid.UUID,
    ) -> UserSkillPublic:
        skill = self.user_skill_repository.get_by_id(
            skill_id=skill_id,
        )
        if not skill:
            raise UserSkillNotFoundError()

        return UserSkillPublic.model_validate(
            skill,
        )

    def delete_skill(
        self,
        *,
        user_profile: UserProfile,
        skill_id: uuid.UUID,
    ) -> None:
        skill = self.__get_skill_by_id(skill_id=skill_id)

        if skill.user_profile_id != user_profile.id:
            raise ForbiddenAction()

        self.user_skill_repository.delete(
            skill_db=skill,
        )

    def update_skill(
        self,
        *,
        user_profile: UserProfile,
        skill_id: uuid.UUID,
        skill_in: UserSkillUpdate,
    ) -> UserSkillPublic:
        skill = self.__get_skill_by_id(skill_id=skill_id)

        if skill.user_profile_id != user_profile.id:
            raise ForbiddenAction()

        skill = self.user_skill_repository.update(
            skill_db=skill,
            skill_in=skill_in,
        )

        return UserSkillPublic.model_validate(
            skill,
        )

    # Private helper functions
    def __get_user_by_username(
        self,
        *,
        username: str,
    ) -> User:
        user = self.user_repository.get_by_username(
            username=username,
        )
        if not user:
            raise UserNotFoundError()

        return user

    def __get_user_profile_by_user_id(
        self,
        *,
        user_id: uuid.UUID,
    ) -> UserProfile:
        profile = self.user_profile_repository.get_by_user_id(
            user_id=user_id,
        )
        if not profile:
            raise UserProfileNotFoundError()

        return profile

    def __get_skill_by_id(
        self,
        *,
        skill_id: uuid.UUID,
    ) -> UserSkill:
        skill = self.user_skill_repository.get_by_id(
            skill_id,
        )
        if not skill:
            raise UserSkillNotFoundError()

        return skill
