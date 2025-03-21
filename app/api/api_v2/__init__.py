from fastapi import APIRouter

from app.core.config import settings
from .users_endpoints import router as users_router
from .base_endpoints import router as base_router
from .json_helper import get_data_from_json

router = APIRouter(
    prefix=settings.api.v2.prefix,
)

router.include_router(
    users_router,
    prefix=settings.api.v2.users,
)
