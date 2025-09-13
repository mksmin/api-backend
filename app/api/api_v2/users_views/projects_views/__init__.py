from fastapi import APIRouter

from .user_projects import router as projects_router

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

router.include_router(
    projects_router,
)
