import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from models.message import Message
from models.user_experience import (
    UserExperienceIn,
    UserExperiencePublic,
    UserExperiencesPublic,
    UserExperienceUpdate,
)
from models.user_profile import UserProfile
from routers.dependencies import get_current_user_profile, get_user_profile_service
from services.user_profile import UserProfileService

router = APIRouter(
    tags=["user-experience"],
)


@router.get(
    "/by-username/{username}",
    response_model=UserExperiencesPublic,
)
def get_user_experiences(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    username: str,
) -> Any:
    return user_profile_service.get_all_experiences_by_username(
        username=username,
    )


@router.post(
    "/",
    response_model=UserExperiencePublic,
)
def add_experience(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    experience_in: UserExperienceIn,
) -> Any:
    """
    Add new user experience.
    """
    return user_profile_service.add_experience(
        user_profile=user_profile,
        experience_in=experience_in,
    )


@router.get(
    "/{experience_id}",
    response_model=UserExperiencePublic,
)
def get_experience_by_id(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    experience_id: uuid.UUID,
) -> Any:
    return user_profile_service.get_experience_by_id(
        experience_id=experience_id,
    )


@router.put(
    "/{experience_id}",
    response_model=UserExperiencePublic,
)
def update_experience(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    experience_id: uuid.UUID,
    experience_in: UserExperienceUpdate,
) -> Any:
    return user_profile_service.update_experience(
        user_profile=user_profile,
        experience_id=experience_id,
        experience_in=experience_in,
    )


@router.delete(
    "/{experience_id}",
    response_model=Message,
)
def delete_experience(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    experience_id: uuid.UUID,
) -> Any:
    user_profile_service.delete_experience(
        user_profile=user_profile,
        experience_id=experience_id,
    )
    return Message(
        message="User Experience deleted.",
    )
