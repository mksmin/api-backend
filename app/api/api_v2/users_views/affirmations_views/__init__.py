from fastapi import APIRouter

from .affirmation_view import router as affirmation_router

router = APIRouter(
    prefix="/affirmations",
    tags=["Affirmations"],
)

router.include_router(
    affirmation_router,
)
