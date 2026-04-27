import uuid
from typing import Sequence

from models.user_link import UserLink, UserLinkUpdate
from repositories.user_link import UserLinkRepository
from sqlmodel import Session, col, select


class PostgresUserLinkRepository(UserLinkRepository):
    def __init__(
        self,
        engine,
    ) -> None:
        self.engine = engine

    def get_all_by_user_profile_id(
        self,
        user_profile_id: uuid.UUID,
    ) -> Sequence[UserLink]:
        with Session(self.engine) as session:
            statement = (
                select(UserLink)
                .order_by(col(UserLink.created_at).desc())
                .where(UserLink.user_profile_id == user_profile_id)
            )

            user_links = session.exec(statement).all()

            return user_links

    def get_by_id(
        self,
        link_id: uuid.UUID,
    ) -> UserLink | None:
        with Session(self.engine) as session:
            return session.get(UserLink, link_id)

    def add(
        self,
        link_in: UserLink,
    ) -> UserLink:
        with Session(self.engine) as session:
            session.add(link_in)
            session.commit()
            session.refresh(link_in)

            return link_in

    def update(
        self,
        link_db: UserLink,
        link_in: UserLinkUpdate,
    ) -> UserLink:
        with Session(self.engine) as session:
            update_data = link_in.model_dump(
                exclude_unset=True,
            )

            link_db.sqlmodel_update(update_data)
            session.add(link_db)
            session.commit()
            session.refresh(link_db)

            return link_db

    def delete(
        self,
        link_db: UserLink,
    ) -> None:
        with Session(self.engine) as session:
            session.delete(link_db)
            session.commit()
