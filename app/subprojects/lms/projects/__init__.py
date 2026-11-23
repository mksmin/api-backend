from fastapi import APIRouter

from subprojects.lms.projects.create import router as project_create_router
from subprojects.lms.projects.detail import router as project_detail_router
from subprojects.lms.projects.flows import router as flows_router
from subprojects.lms.projects.participants import router as participants_router

router = APIRouter(
    prefix="/projects",
)

router.include_router(
    project_create_router,
)
router.include_router(
    project_detail_router,
)

router.include_router(
    flows_router,
)
router.include_router(
    participants_router,
)
