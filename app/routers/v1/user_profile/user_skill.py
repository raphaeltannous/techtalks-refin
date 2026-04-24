import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from models.message import Message
from models.user_profile import UserProfile
from models.user_skill import (
    UserSkillIn,
    UserSkillPublic,
    UserSkillsPublic,
    UserSkillUpdate,
)
from routers.dependencies import get_current_user_profile, get_user_profile_service
from services.user_profile import UserProfileService

router = APIRouter(
    tags=["user-skill"],
)


@router.get(
    "/by-username/{username}",
    response_model=UserSkillsPublic,
)
def get_user_skills(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    username: str,
) -> Any:
    return user_profile_service.get_all_skills_by_username(
        username=username,
    )


@router.post(
    "/",
    response_model=UserSkillPublic,
)
def add_skill(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    skill_in: UserSkillIn,
) -> Any:
    """
    Add new user skill.
    """
    return user_profile_service.add_skill(
        user_profile=user_profile,
        skill_in=skill_in,
    )


@router.get(
    "/{skill_id}",
    response_model=UserSkillPublic,
)
def get_skill_by_id(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    skill_id: uuid.UUID,
) -> Any:
    return user_profile_service.get_skill_by_id(
        skill_id=skill_id,
    )


@router.put(
    "/{skill_id}",
    response_model=UserSkillPublic,
)
def update_skill(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    skill_id: uuid.UUID,
    skill_in: UserSkillUpdate,
) -> Any:
    return user_profile_service.update_skill(
        user_profile=user_profile,
        skill_id=skill_id,
        skill_in=skill_in,
    )


@router.delete(
    "/{skill_id}",
    response_model=Message,
)
def delete_skill(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    skill_id: uuid.UUID,
) -> Any:
    user_profile_service.delete_skill(
        user_profile=user_profile,
        skill_id=skill_id,
    )

    return Message(
        message="User skill deleted.",
    )
