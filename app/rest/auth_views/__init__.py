from fastapi import APIRouter

from rest.auth_views.api_key_views import router as api_key_router
from rest.auth_views.tg_auth import router as tg_auth_router

router = APIRouter(
    tags=["Authentication"],
)

router.include_router(
    tg_auth_router,
)
router.include_router(
    api_key_router,
)
