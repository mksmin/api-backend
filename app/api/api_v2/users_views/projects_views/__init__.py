from fastapi import APIRouter

from api.api_v2.users_views.projects_views.create import (
    router as create_project_router,
)
from api.api_v2.users_views.projects_views.delete import (
    router as delete_project_router,
)
from api.api_v2.users_views.projects_views.read import (
    router as get_project_router,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

router.include_router(
    create_project_router,
)
router.include_router(
    get_project_router,
)
router.include_router(
    delete_project_router,
)
