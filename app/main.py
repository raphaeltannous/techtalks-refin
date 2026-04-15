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
from repositories.postgres.user import PostgresUserRepository
from routers.main import api_router
from services.user import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    mail_template_manager = EmailTemplateManager()
    mailer: Mailer = SMTPMailService()

    db.init(postgres_engine)

    # Initialize Repositories
    user_repository = PostgresUserRepository(postgres_engine)

    # Initialize Services
    app.state.user_service = UserService(
        user_repository=user_repository,
        mail_template_manager=mail_template_manager,
        mailer=mailer,
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
    openapi_url=f"{settings.API_VERSION_STRING}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        reload=True,
    )
