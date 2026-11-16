from fastapi import APIRouter

from subprojects.lms.main_views import router as lms_router
from subprojects.lms.projects import router as lms_projects_router

router = APIRouter(
    prefix="/lms",
    tags=["lms"],
)

router.include_router(
    lms_router,
)
router.include_router(
    lms_projects_router,
)
