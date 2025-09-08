from fastapi import APIRouter

from core.config import settings
from api.api_v2.users_views import router as users_router
from .base_endpoints import router as base_router
from .json_helper import get_data_from_json
from .queue_views.rabbit_tasks import router as rabbit_router
from .devs import router as devs_router

router = APIRouter(
    prefix=settings.api.v2.prefix,
)

router.include_router(
    users_router,
)
router.include_router(
    rabbit_router,
    prefix=settings.api.v2.users,
)


if settings.run.dev_mode:
    router.include_router(devs_router)
