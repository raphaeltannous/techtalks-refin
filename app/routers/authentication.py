from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from models.jwt import Token
from models.user import UserPublic, UserRegister
from services.user import UserService

from routers.dependencies import get_user_service

from .dependencies import CurrentUser

router = APIRouter(
    tags=["authentication"],
)


@router.post("/login")
def login(
    *,
    user_repository: Annotated[UserService, Depends(get_user_service)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    return user_repository.authenticate(
        email=form_data.username,
        password=form_data.password,
    )


@router.post(
    "/login/status",
    response_model=UserPublic,
)
def login_status(
    *,
    current_user: CurrentUser,
) -> Any:
    """
    If logged in.
    """
    return current_user


@router.post(
    "/register",
    response_model=UserPublic,
)
def register(
    *,
    user_repository: Annotated[UserService, Depends(get_user_service)],
    user_in: UserRegister,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Register.
    """
    return user_repository.register(
        user_in=user_in,
        background_tasks=background_tasks,
    )
