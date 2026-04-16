from models.password_reset import PasswordReset, PasswordResetUpdate
from repositories.password_reset import PasswordResetRepository
from sqlmodel import Session, select


class PostgresPasswordReset(PasswordResetRepository):
    def __init__(
        self,
        engine,
    ) -> None:
        self.engine = engine

    def get_by_hash(self, hash: str) -> PasswordReset | None:
        with Session(self.engine) as session:
            statement = select(PasswordReset).where(
                PasswordReset.hash == hash,
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
        self, password_reset_db: PasswordReset, password_reset_in: PasswordResetUpdate
    ) -> PasswordReset:
        with Session(self.engine) as session:
            update_data = password_reset_in.model_dump(
                exclude_unset=True,
            )

            password_reset_db.sqlmodel_update(update_data)
            session.add(password_reset_db)
            session.commit()
            session.refresh(password_reset_db)

            return password_reset_db
