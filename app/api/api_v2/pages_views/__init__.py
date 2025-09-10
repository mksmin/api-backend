from fastapi import APIRouter

from .page_views import router as main_pages_router

router = APIRouter()

router.include_router(
    main_pages_router,
)
