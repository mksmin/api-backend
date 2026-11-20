from fastapi import APIRouter

from config import settings

from .affirmations_views import router as user_affirmations_router

router = APIRouter(
    prefix=settings.api.v2.users,
)


router.include_router(
    user_affirmations_router,
)
