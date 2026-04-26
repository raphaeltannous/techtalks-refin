from typing import Annotated, Any

from fastapi import APIRouter, Depends
from models.user_profile import UserProfile, UserProfilePublic, UserProfileUpdate
from routers.dependencies import get_current_user_profile, get_user_profile_service
from services.user_profile import UserProfileService

router = APIRouter()


@router.get(
    "/by-username/{username}",
    response_model=UserProfilePublic,
)
def get_user_profile(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    username: str,
) -> Any:
    return user_profile_service.get_by_username(
        username=username,
    )


@router.put(
    "/",
    response_model=UserProfilePublic,
)
def update_language(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    profile_in: UserProfileUpdate,
) -> Any:
    return user_profile_service.update_profile(
        user_profile=user_profile,
        profile_in=profile_in,
    )
