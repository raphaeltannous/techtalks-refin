import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from models.message import Message
from models.user_link import (
    UserLinkIn,
    UserLinkPublic,
    UserLinksPublic,
    UserLinkUpdate,
)
from models.user_profile import UserProfile
from routers.dependencies import get_current_user_profile, get_user_profile_service
from services.user_profile import UserProfileService

router = APIRouter(
    tags=["user-link"],
)


@router.get(
    "/by-username/{username}",
    response_model=UserLinksPublic,
)
def get_user_links(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    username: str,
) -> Any:
    return user_profile_service.get_all_links_by_username(
        username=username,
    )


@router.post(
    "/",
    response_model=UserLinkPublic,
)
def add_link(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    link_in: UserLinkIn,
) -> Any:
    """
    Add new user link.
    """
    return user_profile_service.add_link(
        user_profile=user_profile,
        link_in=link_in,
    )


@router.get(
    "/{link_id}",
    response_model=UserLinkPublic,
)
def get_link_by_id(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    link_id: uuid.UUID,
) -> Any:
    return user_profile_service.get_link_by_id(
        link_id=link_id,
    )


@router.put(
    "/{link_id}",
    response_model=UserLinkPublic,
)
def update_link(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    link_id: uuid.UUID,
    link_in: UserLinkUpdate,
) -> Any:
    return user_profile_service.update_link(
        user_profile=user_profile,
        link_id=link_id,
        link_in=link_in,
    )


@router.delete(
    "/{link_id}",
    response_model=Message,
)
def delete_link(
    *,
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    user_profile: Annotated[UserProfile, Depends(get_current_user_profile)],
    link_id: uuid.UUID,
) -> Any:
    user_profile_service.delete_link(
        user_profile=user_profile,
        link_id=link_id,
    )
    return Message(
        message="User link deleted.",
    )
