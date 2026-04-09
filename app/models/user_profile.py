import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic.alias_generators import to_snake
from sqlalchemy import DateTime
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from user import User
    from user_certificate import UserCertificate
    from user_experience import UserExperience
    from user_language import UserLanguage
    from user_link import UserLink
    from user_project import UserProject
    from user_skill import UserSkill
    from user_education import UserEducation


class UserProfileBase(SQLModel):
    headline: str | None = Field(default=None, max_length=100)
    about: str | None = Field(default=None, max_length=1_000)
    location: str | None = Field(default=None, max_length=200)


class UserProfile(UserProfileBase, table=True):
    @declared_attr.directive  # type: ignore[misc]
    @classmethod
    def __tablename__(cls) -> str:  # pyright: ignore[reportIncompatibleVariableOverride]
        return to_snake(cls.__name__)

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True,
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
        sa_type=DateTime(timezone=True),  #  type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),  #  type: ignore
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )

    user: "User" = Relationship(
        back_populates="user_profile",
    )
    user_links: list["UserLink"] = Relationship(
        back_populates="user_profile",
    )
    user_projects: list["UserProject"] = Relationship(
        back_populates="user_profile",
    )
    user_certifications: list["UserCertificate"] = Relationship(
        back_populates="user_profile",
    )
    user_languages: list["UserLanguage"] = Relationship(
        back_populates="user_profile",
    )
    user_experiences: list["UserExperience"] = Relationship(
        back_populates="user_profile",
    )
    user_skills: list["UserSkill"] = Relationship(
        back_populates="user_profile",
    )
    user_educations: list["UserEducation"] = Relationship(
        back_populates="user_profile",
    )