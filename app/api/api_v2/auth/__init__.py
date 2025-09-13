__all__ = (
    "api_key_router",
    "auth_router",
    "auth_utils",
    "router",
    "token_utils",
)

from fastapi import APIRouter

from . import access_token_helper as token_utils
from . import auth_handler as auth_utils
from .api_key_endpoints import router as api_key_router
from .auth_endpoints import router as auth_router

router = APIRouter(
    tags=["Authentication"],
)

router.include_router(auth_router)
router.include_router(api_key_router)
