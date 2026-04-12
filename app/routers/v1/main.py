from config import settings
from fastapi import APIRouter

from . import private

api_v1_router = APIRouter()

if settings.ENVIRONMENT == "local":
    api_v1_router.include_router(private.router)
