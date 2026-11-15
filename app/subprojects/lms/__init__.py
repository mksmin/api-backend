from fastapi import APIRouter

from subprojects.lms.main_views import router as lms_router

router = APIRouter(
    prefix="/lms",
    tags=["lms"],
)

router.include_router(
    lms_router,
)
