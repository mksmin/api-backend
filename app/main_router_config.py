import logging

from fastapi import (
    FastAPI,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api import router as api_router
from app_lifespan import lifespan
from core.config import settings
from paths_constants import (
    FRONTEND_DIR_PATH,
)
from rest.auth_views import router as auth_router
from rest.main_views import router as main_views_router
from rest.pages_views import router as pages_router
from rest.redirect import router as redirect_router
from temp_views import router as temp_router

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

main_app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secrets.session_secret,
)

routers_for_include = (
    auth_router,
    api_router,
    redirect_router,
    main_views_router,
    pages_router,
    temp_router,
)

for router in routers_for_include:
    main_app.include_router(router)
