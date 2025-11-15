from fastapi import APIRouter

from misc.rabbitmq_broker import rabbitmq_broker
from rest.pages_views.affirmations_views import router as affirmations_router
from rest.pages_views.login_views import router as auth_router
from rest.pages_views.profile_views import router as profile_router
from rest.pages_views.projects_views import router as projects_router

router = APIRouter(
    tags=["Page views"],
)

router.include_router(
    affirmations_router,
)
router.include_router(
    auth_router,
)
router.include_router(
    projects_router,
)
router.include_router(
    profile_router,
)
router.include_router(
    rabbitmq_broker,
)
