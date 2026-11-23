import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database.db_helper import db_helper
from misc.rabbit_lifecycle import rabbit_background_start

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,  # noqa: ARG001
) -> AsyncGenerator[None]:
    log.info("Start FastAPI")
    try:
        async with asyncio.timeout(5):
            await db_helper.ping()

        async with rabbit_background_start():
            yield

    except ConnectionRefusedError:
        log.critical(
            "Ошибка во время подключения к БД",
            exc_info=True,
        )
        raise
    finally:
        log.info("Stop FastAPI")
        await db_helper.dispose()
