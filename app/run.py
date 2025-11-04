"""
This is the main entry point of the application.
It is responsible for starting the application
"""

import logging
import os
import sys
from typing import Any

import uvicorn

from core.config import console_handler, settings

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
            "host": settings.run.host,
            "port": settings.run.port,
            "log_level": settings.log.level,
            "reload": False,
            "log_config": None,
            "use_colors": True,
            "workers": 1,
            "proxy_headers": True,
            "forwarded_allow_ips": forwarded_allow_ips,
        }
        if not sys.platform.startswith("win") or os.getenv("FORCE_UNIX_SOCKET"):
            run_args["uds"] = "/tmp/uvicorn.sock"  # noqa: S108

        uvicorn.run(**run_args)

    except KeyboardInterrupt:
        log.warning("Exit from app has occurred with KeyboardInterrupt")
    else:
        log.info("Application stopped")
