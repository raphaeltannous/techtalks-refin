import uuid
from datetime import datetime, timezone

from pydantic.alias_generators import to_snake
from sqlalchemy import DateTime
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel


class EmailVerificationBase(SQLModel):
    token_hash: str = Field(
        nullable=False,
        index=True,
        unique=True,
    )

    expires_at: datetime = Field(
        nullable=False,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class EmailVerification(EmailVerificationBase, table=True):
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
        nullable=False,
        unique=True,
        foreign_key="user.id",
        ondelete="CASCADE",
    )

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class EmailVerificationUpdate(SQLModel):
    token_hash: str | None = Field(
        default=None,
        nullable=True,
    )
    expires_at: datetime | None = Field(
        default=None,
        nullable=True,
    )


class EmailVerificationConfirm(SQLModel):
    token: str = Field(nullable=False)
