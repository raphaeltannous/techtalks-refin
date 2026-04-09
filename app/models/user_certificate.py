import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic.alias_generators import to_snake
from sqlalchemy import DateTime
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from user_profile import UserProfile


class UserCertificateBase(SQLModel):
    name: str = Field(max_length=100)
    issuing_organization: str = Field(max_length=100)

    issuing_date: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    expire_date: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    credential_id: str = Field(max_length=80)
    credential_url: str = Field(max_length=500)


class UserCertificate(UserCertificateBase, table=True):
    @declared_attr.directive  # type: ignore[misc]
    @classmethod
    def __tablename__(cls) -> str:  # pyright: ignore[reportIncompatibleVariableOverride]
        return to_snake(cls.__name__)

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        index=True,
        primary_key=True,
    )
    user_profile_id: uuid.UUID = Field(
        index=True,
        nullable=False,
        foreign_key="user_profile.id",
        ondelete="CASCADE",
    )

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),  #  type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),  #  type: ignore
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )

    user_profile: UserProfile = Relationship(
        back_populates="user_certifications",
    )
