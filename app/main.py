import logging
import pathlib
from contextlib import asynccontextmanager

from config import settings
from db import db, db_data
from db.postgres import engine as postgres_engine
from fastapi import FastAPI
from mail.mailer import Mailer
from mail.smtp import SMTPMailService
from mail.template_manager import EmailTemplateManager
from repositories.postgres.email_verification import PostgresEmailVerificationRepository
from repositories.postgres.password_reset import PostgresPasswordResetRepository
from repositories.postgres.user import PostgresUserRepository
from repositories.postgres.user_language import PostgresUserLanguageRepository
from repositories.postgres.user_link import PostgresUserLinkRepository
from repositories.postgres.user_profile import PostgresUserProfileRepository
from repositories.postgres.user_skill import PostgresUserSkillRepository
from routers.main import api_router
from services.user import UserService
from services.user_profile import UserProfileService


@asynccontextmanager
async def lifespan(app: FastAPI):
    mail_template_manager = EmailTemplateManager()
    mailer: Mailer = SMTPMailService()

    db.init(postgres_engine)

    # Initialize Repositories
    user_repository = PostgresUserRepository(postgres_engine)
    password_reset_repository = PostgresPasswordResetRepository(postgres_engine)
    email_verification_repository = PostgresEmailVerificationRepository(postgres_engine)

    user_profile_repository = PostgresUserProfileRepository(postgres_engine)
    user_skill_repository = PostgresUserSkillRepository(postgres_engine)
    user_language_repository = PostgresUserLanguageRepository(postgres_engine)
    user_link_repository = PostgresUserLinkRepository(postgres_engine)

    # Initialize Services
    app.state.user_service = UserService(
        user_repository=user_repository,
        password_reset_repository=password_reset_repository,
        email_verification_repository=email_verification_repository,
        mail_template_manager=mail_template_manager,
        mailer=mailer,
    )

    app.state.user_profile_service = UserProfileService(
        user_repository=user_repository,
        user_skill_repository=user_skill_repository,
        user_profile_repository=user_profile_repository,
        user_language_repository=user_language_repository,
        user_link_repository=user_link_repository,
    )

    db_data.init(app.state.user_service)

    # Logging
    logger = logging.getLogger("uvicorn.error")

    config_path: pathlib.Path = pathlib.Path(__file__)
    root_project: pathlib.Path = pathlib.Path(config_path.parent).parent
    log_directory = root_project.joinpath("logs")
    log_directory.mkdir(parents=True, exist_ok=True)
    log_file = log_directory.joinpath("app.log")

    file_handler = logging.FileHandler(
        str(log_file),
        mode="a",
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        ),
    )

    logger.addHandler(file_handler)

    yield

    logger.removeHandler(file_handler)
    file_handler.close()

    postgres_engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_VERSION_1_STRING}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        reload=True,
    )
