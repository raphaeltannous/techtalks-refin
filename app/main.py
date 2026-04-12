from contextlib import asynccontextmanager

from config import settings
from db import db, db_data
from db.postgres import engine as postgres_engine
from fastapi import FastAPI
from repositories.postgres.user import PostgresUserRepository
from routers.main import api_router
from services.user import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init(postgres_engine)

    # Initialize Repositories
    user_repository = PostgresUserRepository(postgres_engine)

    # Initialize Services
    app.state.user_service = UserService(user_repository=user_repository)

    db_data.init(app.state.user_service)

    yield

    postgres_engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_VERSION_STRING}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
