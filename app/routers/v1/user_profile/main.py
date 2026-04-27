from fastapi import APIRouter

from .user_language import router as user_language_router
from .user_link import router as user_link_router
from .user_profile import router as user_profile_router
from .user_skill import router as user_skill_router

main_user_profile_router = APIRouter(
    tags=["user-profile"],
)

main_user_profile_router.include_router(
    user_profile_router,
    prefix="/profile",
)
main_user_profile_router.include_router(
    user_skill_router,
    prefix="/skill",
)
main_user_profile_router.include_router(
    user_language_router,
    prefix="/language",
)
main_user_profile_router.include_router(
    user_link_router,
    prefix="/link",
)
