import uuid
from datetime import datetime, timezone

from pydantic.alias_generators import to_snake
from sqlalchemy import DateTime
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel


class UserEducationBase(SQLModel):
    school: str = Field(max_length=100)
    degree: str = Field(max_length=100)
    major: str = Field(max_length=100)
    start_date: datetime = Field(sa_type=DateTime(timezone=True))  # type: ignore
    end_date: datetime = Field(sa_type=DateTime(timezone=True))  # type: ignore
    grade: int
    description: str | None = Field(default=None, max_length=1000)


class UserEducation(UserEducationBase, table=True):
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
