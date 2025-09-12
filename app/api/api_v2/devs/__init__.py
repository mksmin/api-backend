from fastapi import APIRouter

from .devs_views import router as devs_main_router

router = APIRouter(
    prefix="/devs",
    tags=["Devs API"],
)

router.include_router(
    devs_main_router,
)
