from fastapi import APIRouter

from rest.auth_views.user_credentials.create import router as create_credential_router

router = APIRouter()

router.include_router(
    create_credential_router,
)
