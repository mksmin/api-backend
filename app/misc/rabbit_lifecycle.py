import asyncio
import logging
from contextlib import asynccontextmanager
from contextlib import suppress
from typing import AsyncGenerator

from misc.rabbitmq_broker import broker

log = logging.getLogger(__name__)


async def _connect_broker() -> None:
    while True:
        try:
            await broker.connect()
        except Exception:
            log.exception("Failed to connect to RabbitMQ")
            await asyncio.sleep(5)
        else:
            return


@asynccontextmanager
async def rabbit_background_start() -> AsyncGenerator[None]:
    task = asyncio.create_task(_connect_broker())
    try:
        yield
    finally:
        task.cancel()

        with suppress(asyncio.CancelledError):
            await task

        await broker.stop()
