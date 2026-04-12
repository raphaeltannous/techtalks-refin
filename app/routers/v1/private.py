from typing import Annotated, Any

from fastapi import APIRouter, Depends
from models.user import User, UsersPublic
from routers.deps import get_user_service
from services.user import UserService

router = APIRouter(prefix="/private", tags=["private"])


@router.get(
    "/users/public",
    response_model=UsersPublic,
)
def get_public_users(
    *,
    user_service: Annotated[UserService, Depends(get_user_service)],
    offset: int = 0,
    limit: int = 25,
) -> Any:
    """
    Retrieve public users.
    """
    return user_service.get_public_users(offset, limit)


@router.get(
    "/users/private",
    response_model=tuple[list[User], int],
)
def get_private_users(
    *,
    user_service: Annotated[UserService, Depends(get_user_service)],
    offset: int = 0,
    limit: int = 25,
) -> Any:
    """
    Retrieve private users.
    """
    return user_service.get_private_users(offset, limit)
