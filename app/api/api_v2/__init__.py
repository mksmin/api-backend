from fastapi import APIRouter

from api.api_v2.users_views import router as users_router
from config import settings

from .devs import router as devs_router

router = APIRouter(
    prefix=settings.api.v2.prefix,
)

router.include_router(
    users_router,
)


if settings.run.dev_mode:
    router.include_router(devs_router)
