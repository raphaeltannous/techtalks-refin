from config import settings
from db import db, db_data
from fastapi import FastAPI
from routers.main import api_router

# Initializing DB
db.init()
db_data.init()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_VERSION_STRING}/openapi.json",
)

app.include_router(api_router, prefix=settings.API_VERSION_STRING)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
