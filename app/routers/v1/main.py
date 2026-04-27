from config import settings
from fastapi import APIRouter

from . import private
from .user_profile.main import main_user_profile_router

api_v1_router = APIRouter()

api_v1_router.include_router(main_user_profile_router, prefix="/user")

if settings.ENVIRONMENT == "local":
    api_v1_router.include_router(private.router)
