import uuid

from models.password_reset import PasswordReset, PasswordResetUpdate
from repositories.password_reset import PasswordResetRepository
from sqlmodel import Session, select


class PostgresPasswordResetRepository(PasswordResetRepository):
    def __init__(
        self,
        engine,
    ) -> None:
        self.engine = engine

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> PasswordReset | None:
        with Session(self.engine) as session:
            statement = select(PasswordReset).where(
                PasswordReset.user_id == user_id,
            )

            password_reset = session.exec(statement).first()

            return password_reset

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> PasswordReset | None:
        with Session(self.engine) as session:
            statement = select(PasswordReset).where(
                PasswordReset.token_hash == token_hash,
            )

            password_reset = session.exec(statement).first()

            return password_reset

    def add(self, password_reset_in: PasswordReset) -> PasswordReset:
        with Session(self.engine) as session:
            session.add(password_reset_in)
            session.commit()
            session.refresh(password_reset_in)

            return password_reset_in

    def update(
        self,
        db_obj: PasswordReset,
        obj_in: PasswordResetUpdate,
    ) -> PasswordReset:
        with Session(self.engine) as session:
            update_data = obj_in.model_dump(
                exclude_unset=True,
            )

            db_obj.sqlmodel_update(update_data)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)

            return db_obj
