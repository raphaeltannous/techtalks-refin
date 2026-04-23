from config import settings
from fastapi import APIRouter

from . import private
from .user_profile.main import user_profile_router

api_v1_router = APIRouter()

api_v1_router.include_router(user_profile_router, prefix="/user-profile")

if settings.ENVIRONMENT == "local":
    api_v1_router.include_router(private.router)
