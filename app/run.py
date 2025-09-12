"""
This is the main entry point of the application. It is responsible for starting the application
"""

import os
import sys

# import libraries
import uvicorn

# import from libraries
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path


# import from modules
from core import logger, settings, db_helper
from api import router as api_router
from api.redirect import router as redirect_router
from api.api_v2.main_views import router as main_router
from api.api_v2.pages_views import router as pages_router
from api.api_v2.auth import router as auth_router

from fastapi.middleware.cors import CORSMiddleware

PATH_DEV = Path(__file__).parent.parent.parent / "api-frontend"
PATH_PROD = Path(__file__).parent.parent.parent / "frontend"
PATH_STATIC = PATH_DEV if settings.run.dev_mode else PATH_PROD


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    WIP

    This function executes the code before 'yield' before running FastAPI
    and code after 'yield' after the FastAPI stops
    :return: None
    """
    logger.info("Start FastAPI")
    yield
    logger.info("Stop FastAPI")
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
    docs_url=None if not settings.run.dev_mode else "/docs",
    redoc_url=None,
    openapi_url=None if not settings.run.dev_mode else "/openapi.json",
    convert_underscores=False,
)

main_app.mount(
    "/static",
    StaticFiles(directory=PATH_STATIC / "public", html=True),
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
        run_args = {
            "app": "run:main_app",
            "host": settings.run.host,
            "port": settings.run.port,
            "log_level": settings.run.log_level,
            "reload": False,
            "log_config": str(Path(__file__).parent / "core/log_conf.json"),
            "use_colors": True,
            "workers": 1,
        }
        if not sys.platform.startswith("win") or os.getenv("FORCE_UNIX_SOCKET"):
            run_args["uds"] = "/tmp/uvicorn.sock"

        uvicorn.run(**run_args)

    except KeyboardInterrupt:
        logger.warning("Exit from app has occurred with KeyboardInterrupt")
    except Exception as e:
        logger.exception("Exception has occurred: %s", e)
    else:
        logger.info("Application stopped")
