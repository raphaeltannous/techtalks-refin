import uuid
from typing import Sequence

from models.user_experience import UserExperience, UserExperienceUpdate
from repositories.user_experience import UserExperienceRepository
from sqlmodel import Session, col, select


class PostgresUserExperienceRepository(UserExperienceRepository):
    def __init__(
        self,
        engine,
    ) -> None:
        self.engine = engine

    def get_all_by_user_profile_id(
        self,
        user_profile_id: uuid.UUID,
    ) -> Sequence[UserExperience]:
        with Session(self.engine) as session:
            statement = (
                select(UserExperience)
                .order_by(col(UserExperience.created_at).desc())
                .where(UserExperience.user_profile_id == user_profile_id)
            )

            user_experiences = session.exec(statement).all()

            return user_experiences

    def get_by_id(
        self,
        experience_id: uuid.UUID,
    ) -> UserExperience | None:
        with Session(self.engine) as session:
            return session.get(UserExperience, experience_id)

    def add(
        self,
        experience_in: UserExperience,
    ) -> UserExperience:
        with Session(self.engine) as session:
            session.add(experience_in)
            session.commit()
            session.refresh(experience_in)

            return experience_in

    def update(
        self,
        experience_db: UserExperience,
        experience_in: UserExperienceUpdate,
    ) -> UserExperience:
        with Session(self.engine) as session:
            update_data = experience_in.model_dump(
                exclude_unset=True,
            )

            experience_db.sqlmodel_update(update_data)
            session.add(experience_db)
            session.commit()
            session.refresh(experience_db)

            return experience_db

    def delete(
        self,
        experience_db: UserExperience,
    ) -> None:
        with Session(self.engine) as session:
            session.delete(experience_db)
            session.commit()

    