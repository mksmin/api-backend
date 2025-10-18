from fastapi import APIRouter

from api.api_v2.users_views.projects_views.list_views import (
    router as projects_list_views_router,
)

from .user_projects import router as projects_router

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

router.include_router(
    projects_router,
)
router.include_router(
    projects_list_views_router,
)
