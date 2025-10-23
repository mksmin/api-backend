from fastapi import APIRouter

from rest.pages_views.affirmations_view import router as affirmations_router
from rest.pages_views.auth_views import router as auth_router
from rest.pages_views.projects_views import router as projects_router

router = APIRouter()

router.include_router(
    affirmations_router,
)
router.include_router(
    auth_router,
)
router.include_router(
    projects_router,
)
