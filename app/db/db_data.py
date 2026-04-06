import crud.users
from config import settings
from models.users import User, UserCreate
from sqlmodel import Session, select

from .engine import engine


def init() -> None:
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == settings.FIRST_ADMIN_EMAIL)
        ).first()
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_ADMIN_EMAIL,
                username=settings.FIRST_ADMIN_USERNAME,
                password=settings.FIRST_ADMIN_PASSWORD,
                is_admin=True,
            )
            user = crud.users.create_user(session=session, user_create=user_in)
