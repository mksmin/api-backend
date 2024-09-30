"""
This is the main entry point of the application. It is responsible for starting the application
"""

# import libraries
import asyncio
import logging
import uvicorn

# import from libraries
from fastapi import FastAPI

# import from modules
from app.config.config import logger
from app.database.models import async_main
from fastapi import FastAPI
from app.api.get_endpoints import getapp
from app.api.post_endpoints import postapp

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(getapp)
app.include_router(postapp)


async def main() -> None:
    try:
        await async_main()
    except Exception as e:
        logger.exception('Проблема с базой данных:', e)
    else:
        logger.info('Start database')


if __name__ == '__main__':
    FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
    logging.basicConfig(format=FORMAT,
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
    try:
        asyncio.run(main())
        uvicorn.run("run:app", host='127.0.0.1', port=8000, log_level="info", reload=False)
    except KeyboardInterrupt:
        logger.warning('Произошел выход из программы KeyboardInterrupt')
