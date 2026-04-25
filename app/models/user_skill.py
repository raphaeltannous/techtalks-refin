import uuid
from datetime import datetime, timezone

from pydantic.alias_generators import to_snake
from sqlalchemy import DateTime
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel


class UserSkillBase(SQLModel):
    # TODO: add min_length=2
    skill: str = Field(max_length=50)


class UserSkill(UserSkillBase, table=True):
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


class UserSkillIn(UserSkillBase):
    pass


class UserSkillUpdate(UserSkillBase):
    pass


class UserSkillPublic(UserSkillBase):
    id: uuid.UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserSkillsPublic(SQLModel):
    skills: list[UserSkillPublic]
