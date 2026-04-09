import uuid
from typing import Any

import crud.users
import security.password_hashing
from fastapi import APIRouter, Depends, HTTPException, status
from models.message import Message
from models.user import (
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from sqlmodel import col, func, select

from .deps import CurrentUser, SessionDep, get_current_active_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/", dependencies=[Depends(get_current_active_admin)], response_model=UsersPublic
)
def read_users(*, session: SessionDep, offset: int = 0, limit: int = 25) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = (
        select(User).order_by(col(User.created_at).desc()).offset(offset).limit(limit)
    )

    users = session.exec(statement).all()

    users_public = [UserPublic.model_validate(user) for user in users]

    return UsersPublic(users=users_public, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_admin)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = crud.users.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    user = crud.users.create_user(session=session, user_create=user_in)
    # TODO: You might want to add email verification.
    # Or send a welcome email.

    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.users.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    # Shouldn't these be in the crud section?
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.get("/me", response_model=UserPublic)
def read_user_me(*, current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    verified, _ = security.password_hashing.verify_password(
        body.current_password, current_user.hashed_password
    )
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current one",
        )

    hashed_password = security.password_hashing.get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in and admin.
    """
    user = crud.users.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    user_create = UserCreate.model_validate(user_in)
    user = crud.users.create_user(session=session, user_create=user_create)
    # TODO: You might want to send an welcome email or verify.
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user

    # If user is not admin, he is not allowed to get
    # another user's data.
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_admin)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this id does not exist in the system",
        )

    if user_in.email:
        existing_user = crud.users.get_user_by_email(
            session=session,
            email=user_in.email,
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

    db_user = crud.users.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_admin)],
)
def delete_user(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
) -> Message:
    """
    Delete a user.
    """

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user == current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins are not allowed to delete themselves",
        )

    session.delete(user)
    session.commit()
    return Message(
        message="User deleted successfully",
    )
