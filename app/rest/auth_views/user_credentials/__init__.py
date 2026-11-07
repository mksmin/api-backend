from fastapi import APIRouter

from rest.auth_views.user_credentials.authenticate import (
    router as authenticate_credential_router,
)
from rest.auth_views.user_credentials.create import router as create_credential_router

router = APIRouter()

router.include_router(
    create_credential_router,
)
router.include_router(
    authenticate_credential_router,
)
