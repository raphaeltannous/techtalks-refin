import uuid

from models.user_profile import UserProfile
from repositories.user_profile import UserProfileRepository
from sqlmodel import Session, select


class PostgresUserProfileRepository(UserProfileRepository):
    def __init__(
        self,
        engine,
    ) -> None:
        self.engine = engine

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> UserProfile | None:
        with Session(self.engine) as session:
            statement = select(UserProfile).where(UserProfile.user_id == user_id)

            user_profile = session.exec(statement).first()

            return user_profile
