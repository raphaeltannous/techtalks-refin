from fastapi import APIRouter

from .user_skill import router as user_skill_router

user_profile_router = APIRouter(
    tags=["user-profile"],
)

user_profile_router.include_router(
    user_skill_router,
    prefix="/user-skill",
)
