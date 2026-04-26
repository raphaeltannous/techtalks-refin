import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from models.message import Message
from models.user_language import (
    UserLanguageIn,
    UserLanguagePublic,
    UserLanguagesPublic,
    UserLanguageUpdate,
)
from models.user_profile import UserProfile
from routers.dependencies import get_current_user_profile, get_user_profile_service
from services.user_profile import UserProfileService

router = APIRouter(
    tags=["user-language"],
)


@router.get(
    "/by-username/{username}",
    response_model=UserLanguagesPublic,
)
def get_user_languages(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    username: str,
) -> Any:
    return user_profile_service.get_all_languages_by_username(
        username=username,
    )


@router.post(
    "/",
    response_model=UserLanguagePublic,
)
def add_language(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    language_in: UserLanguageIn,
) -> Any:
    """
    Add new user language.
    """
    return user_profile_service.add_language(
        user_profile=user_profile,
        language_in=language_in,
    )


@router.get(
    "/{language_id}",
    response_model=UserLanguagePublic,
)
def get_language_by_id(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    language_id: uuid.UUID,
) -> Any:
    return user_profile_service.get_language_by_id(
        language_id=language_id,
    )


@router.put(
    "/{language_id}",
    response_model=UserLanguagePublic,
)
def update_language(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    language_id: uuid.UUID,
    language_in: UserLanguageUpdate,
) -> Any:
    return user_profile_service.update_language(
        user_profile=user_profile,
        language_id=language_id,
        language_in=language_in,
    )


@router.delete(
    "/{language_id}",
    response_model=Message,
)
def delete_language(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    language_id: uuid.UUID,
) -> Any:
    user_profile_service.delete_language(
        user_profile=user_profile,
        language_id=language_id,
    )

    return Message(
        message="User language deleted.",
    )
