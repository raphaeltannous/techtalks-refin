from models.email_verification import EmailVerification, EmailVerificationUpdate
from repositories.email_verification import EmailVerificationRepository
from sqlmodel import Session, select


class PostgresEmailVerification(EmailVerificationRepository):
    def __init__(
        self,
        engine,
    ) -> None:
        self.engine = engine

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> EmailVerification | None:
        with Session(self.engine) as session:
            statement = select(EmailVerification).where(
                EmailVerification.token_hash == token_hash
            )

            email_verification = session.exec(statement).first()

            return email_verification

    def add(
        self,
        email_verification_in: EmailVerification,
    ) -> EmailVerification:
        with Session(self.engine) as session:
            session.add(email_verification_in)
            session.commit()
            session.refresh(email_verification_in)

            return email_verification_in

    def update(
        self,
        db_obj: EmailVerification,
        obj_in: EmailVerificationUpdate,
    ) -> EmailVerification:
        with Session(self.engine) as session:
            update_data = obj_in.model_dump(exclude_unset=True)

            db_obj.sqlmodel_update(update_data)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)

            return db_obj
