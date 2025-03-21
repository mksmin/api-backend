import traceback
from dateutil import parser

import asyncpg

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.core.database import User, Project
from .config import connector


@connector
async def create_user_from_dict(
        session: AsyncSession,
        dict_values: dict
) -> tuple[bool, str]:
    valid_data = {
        key:  (
            parser.parse(value)
            if key in ("date_bid_ya", "birth_date")
            else value
        )
        for key, value in dict_values.items()
        if hasattr(User, key)
    }

    try:
        user = User(**valid_data)

        session.add(user)
        await session.commit()
        return True, 'Пользователь успешно создан.'

    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        logger.exception("Проблема с подключением к БД")
        error_msg = f"{type(e).__name__}: {str(e)}"
        return False, error_msg

    except SQLAlchemyError as e:
        logger.exception("Ошибка SQLAlchemy")
        error_msg = f"{type(e).__name__}: {str(e)}"
        return False, error_msg

    except Exception as e:
        # Логируем ошибку с автоматическим добавлением traceback
        logger.exception('Ошибка при создании пользователя')

        # Формируем понятное сообщение об ошибке
        error_msg = f"{type(e).__name__}: {str(e)}"
        return False, error_msg
