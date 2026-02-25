"""
This is the main entry point of the application.
It is responsible for starting the application
"""

import logging
import os
import sys
from typing import Any

import uvicorn

from config import console_handler
from config import settings

logging.basicConfig(
    level=settings.log.level,
    handlers=[console_handler],
)
log = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        forwarded_allow_ips = "*"
        run_args: dict[str, Any] = {
            "app": "main_router_config:main_app",
            "host": settings.uvicorn.host,
            "port": settings.uvicorn.port,
            "log_level": settings.log.level,
            "reload": False,
            "log_config": None,
            "use_colors": True,
            "workers": settings.uvicorn.workers,
            "proxy_headers": True,
            "forwarded_allow_ips": forwarded_allow_ips,
        }

        if settings.uvicorn.unix_socket and (
            not sys.platform.startswith("win") or os.getenv("FORCE_UNIX_SOCKET")
        ):
            run_args["uds"] = "/tmp/uvicorn.sock"  # noqa: S108

        uvicorn.run(**run_args)

    except KeyboardInterrupt:
        log.warning("Exit from app has occurred with KeyboardInterrupt")
    else:
        log.info("Application stopped")
