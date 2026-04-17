import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from user_profile import UserProfile


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, nullable=False, max_length=255)
    name: str | None = Field(default=None, index=True, max_length=75)
    is_active: bool = True
    is_admin: bool = False


class User(UserBase, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        index=True,
        primary_key=True,
    )

    hashed_password: str

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )

    user_profile: "UserProfile" = Relationship(
        back_populates="user",
    )


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=75)


class UserUpdate(UserBase):
    """
    Admin-only user update model.

    Making email optional from UserBase.
    """

    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    hashed_password: str | None = Field(default=None)


class UserUpdateMe(SQLModel):  # Public
    email: EmailStr | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, max_length=75)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    """
    UserPublic returned to the public as json.
    """

    id: uuid.UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UsersPublic(SQLModel):
    users: list[UserPublic]
    count: int
