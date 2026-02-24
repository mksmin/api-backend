from fastapi import APIRouter

from api.api_v2 import router as router_api_v2
from config import settings

router = APIRouter(
    prefix=settings.api.prefix,
)
router.include_router(
    router_api_v2,
)
