import logging
import uuid

from exceptions import (
    ForbiddenAction,
    UserLanguageNotFoundError,
    UserLinkNotFoundError,
    UserNotFoundError,
    UserProfileNotFoundError,
    UserSkillNotFoundError,
)
from models.user import User
from models.user_language import (
    UserLanguage,
    UserLanguageIn,
    UserLanguagePublic,
    UserLanguagesPublic,
    UserLanguageUpdate,
)
from models.user_link import (
    UserLink,
    UserLinkIn,
    UserLinkPublic,
    UserLinksPublic,
    UserLinkUpdate,
)
from models.user_profile import UserProfile, UserProfilePublic, UserProfileUpdate
from models.user_skill import (
    UserSkill,
    UserSkillIn,
    UserSkillPublic,
    UserSkillsPublic,
    UserSkillUpdate,
)
from repositories.user import UserRepository
from repositories.user_language import UserLanguageRepository
from repositories.user_link import UserLinkRepository
from repositories.user_profile import UserProfileRepository
from repositories.user_skill import UserSkillRepository


class UserProfileService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_skill_repository: UserSkillRepository,
        user_profile_repository: UserProfileRepository,
        user_language_repository: UserLanguageRepository,
        user_link_repository: UserLinkRepository,
    ) -> None:
        self.user_repository = user_repository
        self.user_skill_repository = user_skill_repository
        self.user_profile_repository = user_profile_repository
        self.user_language_repository = user_language_repository
        self.user_link_repository = user_link_repository

        self.logger = logging.getLogger("uvicorn.error")

    def get_by_user_id(
        self,
        *,
        user_id: uuid.UUID,
    ) -> UserProfile:
        return self.__get_user_profile_by_user_id(
            user_id=user_id,
        )

    def get_by_username(
        self,
        *,
        username: str,
    ) -> UserProfilePublic:
        user = self.__get_user_by_username(username=username)

        profile = self.get_by_user_id(
            user_id=user.id,
        )

        return UserProfilePublic.model_validate(
            profile,
        )

    def update_profile(
        self,
        *,
        user_profile: UserProfile,
        profile_in: UserProfileUpdate,
    ) -> UserProfilePublic:
        profile = self.user_profile_repository.update(
            profile_db=user_profile,
            profile_in=profile_in,
        )

        return UserProfilePublic.model_validate(
            profile,
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

    def get_skill_by_id(
        self,
        *,
        skill_id: uuid.UUID,
    ) -> UserSkillPublic:
        skill = self.__get_skill_by_id(skill_id=skill_id)

        return UserSkillPublic.model_validate(
            skill,
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

    def get_all_languages_by_username(
        self,
        *,
        username: str,
    ) -> UserLanguagesPublic:
        user = self.__get_user_by_username(
            username=username,
        )

        user_profile = self.__get_user_profile_by_user_id(
            user_id=user.id,
        )

        languages = self.user_language_repository.get_all_by_user_profile_id(
            user_profile.id,
        )

        public_languages = [UserLanguagePublic.model_validate(l) for l in languages]

        return UserLanguagesPublic(
            languages=public_languages,
        )

    def get_language_by_id(
        self,
        *,
        language_id: uuid.UUID,
    ) -> UserLanguagePublic:
        language = self.__get_language_by_id(language_id=language_id)

        return UserLanguagePublic.model_validate(
            language,
        )

    def add_language(
        self,
        *,
        user_profile: UserProfile,
        language_in: UserLanguageIn,
    ) -> UserLanguagePublic:
        language = UserLanguage.model_validate(
            language_in,
            update={
                "user_profile_id": user_profile.id,
            },
        )

        language = self.user_language_repository.add(
            language,
        )

        return UserLanguagePublic.model_validate(
            language,
        )

    def delete_language(
        self,
        *,
        user_profile: UserProfile,
        language_id: uuid.UUID,
    ) -> None:
        language = self.__get_language_by_id(language_id=language_id)

        if language.user_profile_id != user_profile.id:
            raise ForbiddenAction()

        self.user_language_repository.delete(
            language_db=language,
        )

    def update_language(
        self,
        *,
        user_profile: UserProfile,
        language_id: uuid.UUID,
        language_in: UserLanguageUpdate,
    ) -> UserLanguagePublic:
        language = self.__get_language_by_id(language_id=language_id)

        if language.user_profile_id != user_profile.id:
            raise ForbiddenAction()

        language = self.user_language_repository.update(
            language_db=language,
            language_in=language_in,
        )

        return UserLanguagePublic.model_validate(
            language,
        )

    def get_all_links_by_username(
        self,
        *,
        username: str,
    ) -> UserLinksPublic:
        user = self.__get_user_by_username(
            username=username,
        )

        user_profile = self.__get_user_profile_by_user_id(
            user_id=user.id,
        )

        links = self.user_link_repository.get_all_by_user_profile_id(
            user_profile.id,
        )

        public_links = [UserLinkPublic.model_validate(l) for l in links]

        return UserLinksPublic(
            links=public_links,
        )

    def get_link_by_id(
        self,
        *,
        link_id: uuid.UUID,
    ) -> UserLinkPublic:
        link = self.__get_link_by_id(link_id=link_id)

        return UserLinkPublic.model_validate(
            link,
        )

    def add_link(
        self,
        *,
        user_profile: UserProfile,
        link_in: UserLinkIn,
    ) -> UserLinkPublic:
        link = UserLink.model_validate(
            link_in,
            update={
                "user_profile_id": user_profile.id,
            },
        )

        link = self.user_link_repository.add(
            link,
        )

        return UserLinkPublic.model_validate(
            link,
        )

    def delete_link(
        self,
        *,
        user_profile: UserProfile,
        link_id: uuid.UUID,
    ) -> None:
        link = self.__get_link_by_id(link_id=link_id)

        if link.user_profile_id != user_profile.id:
            raise ForbiddenAction()

        self.user_link_repository.delete(
            link_db=link,
        )

    def update_link(
        self,
        *,
        user_profile: UserProfile,
        link_id: uuid.UUID,
        link_in: UserLinkUpdate,
    ) -> UserLinkPublic:
        link = self.__get_link_by_id(link_id=link_id)

        if link.user_profile_id != user_profile.id:
            raise ForbiddenAction()

        link = self.user_link_repository.update(
            link_db=link,
            link_in=link_in,
        )

        return UserLinkPublic.model_validate(
            link,
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

    def __get_user_profile_by_id(
        self,
        *,
        profile_id: uuid.UUID,
    ) -> UserProfile:
        profile = self.user_profile_repository.get_by_id(
            profile_id=profile_id,
        )
        if not profile:
            raise UserProfileNotFoundError()

        return profile

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

    def __get_language_by_id(
        self,
        *,
        language_id: uuid.UUID,
    ) -> UserLanguage:
        language = self.user_language_repository.get_by_id(
            language_id,
        )
        if not language:
            raise UserLanguageNotFoundError()

        return language

    def __get_link_by_id(
        self,
        *,
        link_id: uuid.UUID,
    ) -> UserLink:
        link = self.user_link_repository.get_by_id(
            link_id,
        )
        if not link:
            raise UserLinkNotFoundError()

        return link
