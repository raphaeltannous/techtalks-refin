import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic.alias_generators import to_snake
from sqlalchemy import DateTime
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel


class EmploymentType(str, Enum):
    full_time = "Full-time"
    part_time = "Part-time"
    self_employed = "Self-employed"
    freelance = "Freelance"
    contract = "Contract"
    internship = "Internship"
    apprenticeship = "Apprenticeship"
    seasonal = "Seasonal"


class LocationType(str, Enum):
    on_site = "On-site"
    hybrid = "Hybrid"
    remote = "Remote"


class UserExperienceBase(SQLModel):
    title: str = Field(max_length=100)
    employment_type: EmploymentType
    company: str = Field(max_length=100)

    location: LocationType
    description: str | None = Field(
        default=None,
        max_length=1_000,
    )

    start_date: datetime = Field(
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    end_date: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class UserExperience(UserExperienceBase, table=True):
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
