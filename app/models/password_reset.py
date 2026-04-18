import uuid
from datetime import datetime, timezone

from pydantic import EmailStr, model_validator
from pydantic.alias_generators import to_snake
from sqlalchemy import DateTime
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel
from typing_extensions import Self


class PasswordResetBase(SQLModel):
    token_hash: str = Field(
        index=True,
        unique=True,
        nullable=False,
    )

    expires_at: datetime = Field(
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class PasswordReset(PasswordResetBase, table=True):
    @declared_attr.directive  # type: ignore[misc]
    @classmethod
    def __tablename__(cls) -> str:  # pyright: ignore[reportIncompatibleVariableOverride]
        return to_snake(cls.__name__)

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        index=True,
        primary_key=True,
    )

    user_id: uuid.UUID = Field(
        index=True,
        unique=True,
        nullable=False,
        foreign_key="user.id",
        ondelete="CASCADE",
    )

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class PasswordResetUpdate(SQLModel):
    token_hash: str | None = Field(
        default=None,
        nullable=True,
    )

    expires_at: datetime | None = Field(
        default=None,
        nullable=True,
    )


class PasswordResetRequest(SQLModel):
    email: EmailStr


class PasswordResetRequestUpdate(SQLModel):
    token: str = Field(
        nullable=False,
    )

    password: str = Field(
        min_length=8,
        max_length=125,
    )
    password_confirm: str = Field(
        min_length=8,
        max_length=125,
    )

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
