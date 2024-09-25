import asyncio
import logging
import uvicorn

from app.config.config import get_tokens, logger
from app.database.models import async_main
import app.database.requests as rq
from app.endpoints import app


async def main() -> None:
    try:
        await async_main()
        print('hello')

    except Exception as e:
        logger.exception('Проблема с базой данных:', e)


if __name__ == '__main__':
    FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
    logging.basicConfig(format=FORMAT,
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
    try:
        asyncio.run(main())
        # uvicorn.run(app, host='localhost', port=8000, log_level="info")

    except KeyboardInterrupt:
        logger.warning('Произошел выход из программы KeyboardInterrupt')
