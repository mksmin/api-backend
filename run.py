"""
This is the main entry point of the application. It is responsible for starting the application
"""

# import libraries
import asyncio
import uvicorn
import os

# import from libraries
from fastapi import FastAPI
from contextlib import asynccontextmanager

# import from modules
from app.config.config import logger
from app.database.models import async_main
from app.api.get_endpoints import getapp
from app.api.post_endpoints import postapp

dirname = os.path.dirname(__file__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """
    WIP

    This function executes the code before 'yield' before running FastAPI
    and code after 'yield' after the FastAPI stops
    :param app:
    :return: None
    """
    # WIP
    logger.info('Start FastAPI')

    yield
    logger.info('Stop FastAPI')


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
app.include_router(getapp)
app.include_router(postapp)


async def main() -> None:
    """
    Function starts the database
    :return: None
    """
    try:
        await async_main()
    except Exception as e:
        logger.exception('Проблема с базой данных:', e)
    else:
        logger.info('Start database')


if __name__ == '__main__':
    try:
        asyncio.run(main())
        uvicorn.run("run:app", host='127.0.0.1', port=8000, log_level="info",
                    reload=True,
                    log_config=os.path.join(os.path.normpath(dirname), 'app/config/log_conf.json'),
                    use_colors=True)

    except KeyboardInterrupt:
        logger.warning('Exit from app has occurred with KeyboardInterrupt')
    except Exception as e:
        logger.exception('Exception has occurred:', e)
    else:
        logger.info('Application stopped')
