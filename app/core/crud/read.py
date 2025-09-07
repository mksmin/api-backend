import traceback
from dateutil import parser

import asyncpg
from sqlalchemy import MetaData, Table, select, func

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import logger
from .config import connector


@connector
async def get_registration_stat(session: AsyncSession, name_db: str) -> dict:
    """
    Вернет статистику регистрации пользователей в виде словаря:
    {
        "total_users": int,
        "details": {
            "competention1": int,
        }
    }
    :param session:
    :param name_db:
    :return: Dict
    """

    metadata = MetaData()

    try:
        async with session.bind.connect() as conn:
            registration_table = await conn.run_sync(
                lambda sync_conn: Table(name_db, metadata, autoload_with=sync_conn)
            )

        # Детали по каждой компетенции
        detail_query = (
            select(registration_table.c.track, func.count().label("count"))
            .group_by(registration_table.c.track)
            .order_by(registration_table.c.track)
        )

        # Суммарная статистика
        general_query = select(func.count()).select_from(registration_table)

        # Запрос к базе данных
        result_detail = await session.execute(detail_query)
        result_general = await session.execute(general_query)

        # отправка результата
        return {
            "total_users": result_general.scalar(),
            "details": {row[0]: row[1] for row in result_detail.all()},
        }

    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.warning(
            f"Ошибка при получении данных из таблицы {name_db}: {error_traceback}"
        )
        return {
            "total_users": 0,
            "details": {"error": "Ошибка при получении данных из таблицы"},
        }
