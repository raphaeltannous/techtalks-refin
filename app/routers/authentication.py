from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from models.jwt import Token
from models.user import UserPublic, UserRegister
from services.user import UserService

from routers.deps import get_user_service

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
            detail="Incorret email or password",
        )

    return token


@router.post("/register")
def register(
    *,
    user_repository: Annotated[UserService, Depends(get_user_service)],
    user_in: UserRegister,
    response_model=UserPublic,
) -> Any:
    """
    Register.
    """
    user = user_repository.register(
        user_in=user_in,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    return user
