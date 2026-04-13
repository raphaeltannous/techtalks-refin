from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from models.jwt import Token
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
