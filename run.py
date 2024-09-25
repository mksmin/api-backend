import asyncio
import logging
import uvicorn

from app.config.config import get_tokens, logger
from app.database.models import async_main
from app.endpoints import app

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
        uvicorn.run("run:app", host='127.0.0.1', port=8000, log_level="info", reload=True)

    except KeyboardInterrupt:
        logger.warning('Произошел выход из программы KeyboardInterrupt')

