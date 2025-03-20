from fastapi import APIRouter

from app.core.config import settings
from .users_endpoints import router as users_router
from .base_endpoints import router as base_router

router = APIRouter(
    prefix=settings.api.v2.prefix,
)

router.include_router(
    users_router,
    prefix=settings.api.v2.users,
)
