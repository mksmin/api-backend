import logging

from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from api import router as api_router
from api.api_v2.auth import router as auth_router
from app_lifespan import lifespan
from core.config import settings
from paths_constants import (
    FRONTEND_DIR_PATH,
    not_found_404,
)
from rest.main_views import router as main_views_router
from rest.pages_views import router as pages_router
from rest.redirect import router as redirect_router

log = logging.getLogger(__name__)
main_app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if settings.run.dev_mode else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.run.dev_mode else None,
    convert_underscores=False,
)


main_app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR_PATH / "static",
        html=True,
    ),
)


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "https://api.xn----7sbbe2cen5a.xn--p1ai",
        "https://web.telegram.org",
    ],
    allow_methods=["POST"],
    allow_headers=["X-Client-Source", "Content-Type"],
    expose_headers=["X-Request-ID"],
)


@main_app.exception_handler(StarletteHTTPException)
async def handle_404_exception(
    request: Request,  # noqa: ARG001
    exc: StarletteHTTPException,
) -> FileResponse:
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return FileResponse(path=not_found_404)
    raise exc


routers_for_include = (
    auth_router,
    api_router,
    redirect_router,
    main_views_router,
    pages_router,
)

for router in routers_for_include:
    main_app.include_router(router)
