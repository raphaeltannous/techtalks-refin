from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
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
    token = user_repository.authenticate(
        email=form_data.username,
        password=form_data.password,
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    return token


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
    user = user_repository.register(
        user_in=user_in,
        background_tasks=background_tasks,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    return user
