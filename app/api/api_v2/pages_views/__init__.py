from fastapi import APIRouter

from .affirmations import router as affirmations_router

router = APIRouter()

router.include_router(
    affirmations_router,
)
