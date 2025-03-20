"""
This is the main entry point of the application. It is responsible for starting the application
"""

# import libraries
import uvicorn

# import from libraries
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path

# import from modules
from app.core import logger, settings, db_helper


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """
    WIP

    This function executes the code before 'yield' before running FastAPI
    and code after 'yield' after the FastAPI stops
    :return: None
    """
    logger.info('Start FastAPI')
    yield
    logger.info('Stop FastAPI')
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)


if __name__ == '__main__':
    try:
        uvicorn.run(
            "run:main_app",
            host=settings.run.host,
            port=settings.run.port,
            log_level=settings.run.log_level,
            reload=True,
            log_config=str(Path(__file__).parent / 'app/core/log_conf.json'),
            use_colors=True
        )

    except KeyboardInterrupt:
        logger.warning('Exit from app has occurred with KeyboardInterrupt')
    except Exception as e:
        logger.exception('Exception has occurred:', e)
    else:
        logger.info('Application stopped')
