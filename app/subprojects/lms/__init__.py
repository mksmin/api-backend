from fastapi import APIRouter
from fastapi import Depends

from rest.pages_views.redirect import redirect_to_login_page
from subprojects.lms.main_views import router as lms_router
from subprojects.lms.projects import router as lms_projects_router

router = APIRouter(
    prefix="/lms",
    tags=["lms"],
    dependencies=[
        Depends(
            redirect_to_login_page,
        ),
    ],
)

router.include_router(
    lms_router,
)
router.include_router(
    lms_projects_router,
)
