from fastapi import APIRouter

from .user_language import router as user_language_router
from .user_link import router as user_link_router
from .user_skill import router as user_skill_router

user_profile_router = APIRouter(
    tags=["user-profile"],
)

user_profile_router.include_router(
    user_skill_router,
    prefix="/user-skill",
)
user_profile_router.include_router(
    user_language_router,
    prefix="/user-language",
)
user_profile_router.include_router(
    user_link_router,
    prefix="/user-link",
)
