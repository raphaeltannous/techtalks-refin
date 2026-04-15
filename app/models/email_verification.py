import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic.alias_generators import to_snake
from sqlalchemy import DateTime
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, SQLModel, Session,select

if TYPE_CHECKING:
    from user import User


class EmailVerificationBase(SQLModel):
    token_hash: str = Field(nullable=False, index=True)

    expires_at: datetime = Field(
        nullable=False,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class EmailVerification(EmailVerificationBase, table=True):
    @declared_attr.directive  # type: ignore[misc]
    @classmethod
    def __tablename__(cls) -> str:
        return to_snake(cls.__name__)

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        index=True,
        primary_key=True,
    )

    user_id: uuid.UUID = Field(
        index=True,
        nullable=False,
        foreign_key="user.id",
        ondelete="CASCADE",
    )
    # to prevent reuse of same token
    is_used: bool = Field(default=False)

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    user: "User" = Relationship(
        back_populates="email_verifications",
    )

class EmailVerificationUpdate(SQLModel):
    token_hash: str | None = None
    expires_at: datetime | None = None
    is_used: bool | None = None

def get_token_by_hash(
    session: Session,
    token_hash: str,
) -> EmailVerification | None:
    """
    Fetch verification record using hashed token.
    """
    statement = select(EmailVerification).where(
        EmailVerification.token_hash == token_hash
    )
    return session.exec(statement).first()


def update_email_verification(
    session: Session,
    db_obj: EmailVerification,
    obj_in: EmailVerificationUpdate,
) -> EmailVerification:
    """
    Update email verification record.
    """
    update_data = obj_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_obj, key, value)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj

def mark_token_as_used(
    session: Session,
    db_obj: EmailVerification,
) -> EmailVerification:
    """
    Prevent token reuse after successful verification.
    """
    db_obj.is_used = True

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj