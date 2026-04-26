import uuid
from typing import Sequence

from models.user_language import (
    UserLanguage,
    UserLanguageUpdate,
)
from repositories.user_language import UserLanguageRepository
from sqlmodel import Session, col, select


class PostgresUserLanguageRepository(UserLanguageRepository):
    def __init__(
        self,
        engine,
    ) -> None:
        self.engine = engine

    def get_all_by_user_profile_id(
        self,
        user_profile_id: uuid.UUID,
    ) -> Sequence[UserLanguage]:
        with Session(self.engine) as session:
            statement = (
                select(UserLanguage)
                .order_by(col(UserLanguage.created_at).desc())
                .where(UserLanguage.user_profile_id == user_profile_id)
            )

            user_languages = session.exec(statement).all()

            return user_languages

    def get_by_id(
        self,
        language_id: uuid.UUID,
    ) -> UserLanguage | None:
        with Session(self.engine) as session:
            return session.get(UserLanguage, language_id)

    def add(
        self,
        language_in: UserLanguage,
    ) -> UserLanguage:
        with Session(self.engine) as session:
            session.add(language_in)
            session.commit()
            session.refresh(language_in)

            return language_in

    def update(
        self,
        language_db: UserLanguage,
        language_in: UserLanguageUpdate,
    ) -> UserLanguage:
        with Session(self.engine) as session:
            update_data = language_in.model_dump(
                exclude_unset=True,
            )

            language_db.sqlmodel_update(update_data)
            session.add(language_db)
            session.commit()
            session.refresh(language_db)

            return language_db

    def delete(
        self,
        language_db: UserLanguage,
    ) -> None:
        with Session(self.engine) as session:
            session.delete(language_db)
            session.commit()
