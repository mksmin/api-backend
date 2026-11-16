from fastapi import APIRouter

from subprojects.lms.projects.detail import router as project_detail_router

router = APIRouter(
    prefix="/projects",
)

router.include_router(
    project_detail_router,
)
