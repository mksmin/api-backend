from fastapi import APIRouter

from core import settings

from .projects_views import router as user_projects_router
from .users_endpoints import router as main_users_router

router = APIRouter(
    prefix=settings.api.v2.users,
)

router.include_router(
    main_users_router,
)

router.include_router(
    user_projects_router,
)
