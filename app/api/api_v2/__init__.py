from fastapi import APIRouter

from api.api_v2.users_views import router as users_router
from core.config import settings

from .devs import router as devs_router
from .json_helper import get_data_from_json

router = APIRouter(
    prefix=settings.api.v2.prefix,
)

router.include_router(
    users_router,
)

if settings.run.dev_mode:
    router.include_router(devs_router)
