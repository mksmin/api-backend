__all__ = (
    "api_key_router",
    "auth_router",
    "auth_utils",
    "router",
    "token_utils",
)

from fastapi import APIRouter

from api.api_v2.auth import access_token_helper as token_utils
from api.api_v2.auth import dependencies as auth_utils
from api.api_v2.auth.api_key_views import router as api_key_router
from api.api_v2.auth.auth_views import router as auth_router

router = APIRouter(
    tags=["Authentication"],
)

router.include_router(auth_router)
router.include_router(api_key_router)
