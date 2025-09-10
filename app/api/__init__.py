from fastapi import APIRouter

from core.config import settings
from api.api_v2 import router as router_api_v2


router = APIRouter(
    prefix=settings.api.prefix,
)
router.include_router(
    router_api_v2,
)
