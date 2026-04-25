import uuid
from typing import Sequence

from models.user_skill import (
    UserSkill,
    UserSkillUpdate,
)
from repositories.user_skill import UserSkillRepository
from sqlmodel import Session, col, select


class PostgresUserSkillRepository(UserSkillRepository):
    def __init__(
        self,
        engine,
    ) -> None:
        self.engine = engine

    def get_all_by_user_profile_id(
        self,
        user_profile_id: uuid.UUID,
    ) -> Sequence[UserSkill]:
        with Session(self.engine) as session:
            statement = (
                select(UserSkill)
                .order_by(col(UserSkill.created_at).desc())
                .where(UserSkill.user_profile_id == user_profile_id)
            )

            user_skills = session.exec(statement).all()

            return user_skills

    def get_by_id(
        self,
        skill_id: uuid.UUID,
    ) -> UserSkill | None:
        with Session(self.engine) as session:
            return session.get(UserSkill, skill_id)

    def add(
        self,
        skill_in: UserSkill,
    ) -> UserSkill:
        with Session(self.engine) as session:
            session.add(skill_in)
            session.commit()
            session.refresh(skill_in)

            return skill_in

    def update(
        self,
        skill_db: UserSkill,
        skill_in: UserSkillUpdate,
    ) -> UserSkill:
        with Session(self.engine) as session:
            update_data = skill_in.model_dump(
                exclude_unset=True,
            )

            skill_db.sqlmodel_update(update_data)
            session.add(skill_db)
            session.commit()
            session.refresh(skill_db)

            return skill_db

    def delete(
        self,
        skill_db: UserSkill,
    ) -> None:
        with Session(self.engine) as session:
            session.delete(skill_db)
            session.commit()
