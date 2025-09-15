import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database.db_helper import db_helper

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,  # noqa: ARG001
) -> AsyncGenerator[None, None]:
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
