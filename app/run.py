"""
This is the main entry point of the application.
It is responsible for starting the application
"""

import os
import sys
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import router as api_router
from api.api_v2.auth import router as auth_router
from api.api_v2.main_views import router as main_router
from api.api_v2.pages_views import router as pages_router
from api.redirect import router as redirect_router
from app_lifespan import lifespan
from core import logger
from core.config import BASE_DIR, settings
from paths_constants import FRONTEND_DIR_PATH

main_app = FastAPI(
    lifespan=lifespan,
    docs_url=None if not settings.run.dev_mode else "/docs",
    redoc_url=None,
    openapi_url=None if not settings.run.dev_mode else "/openapi.json",
    convert_underscores=False,
)

main_app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR_PATH / "public",
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

routers_for_include = (
    auth_router,
    api_router,
    redirect_router,
    main_router,
    pages_router,
)

for router in routers_for_include:
    main_app.include_router(router)

if __name__ == "__main__":
    try:
        run_args: dict[str, Any] = {
            "app": "run:main_app",
            "host": settings.run.host,
            "port": settings.run.port,
            "log_level": settings.log.mode.lower(),
            "reload": False,
            "log_config": str(BASE_DIR / "core/log_conf.json"),
            "use_colors": True,
            "workers": 1,
        }
        if not sys.platform.startswith("win") or os.getenv("FORCE_UNIX_SOCKET"):
            run_args["uds"] = "/tmp/uvicorn.sock"  # noqa: S108

        uvicorn.run(**run_args)

    except KeyboardInterrupt:
        logger.warning("Exit from app has occurred with KeyboardInterrupt")
    else:
        logger.info("Application stopped")
