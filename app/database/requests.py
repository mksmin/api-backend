"""
Module with functions for database operations
"""

# import from libraries
from sqlalchemy import select, func
from sqlalchemy.sql import text
from functools import wraps

# import from modules
from app.database.models import async_session
from app.database.models import User


def connection(func) -> None:
    """
    this decorator is used to make the database connection
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return wrapper


@connection
async def set_user_registration(session):
    pass


async def add_column_for_db(session, column_name):
    table_name = User.__tablename__
    text_table = text(f'ALTER TABLE {table_name} ADD {column_name} CHAR(50)')
    await session.execute(text_table)
    await session.commit()


async def get_colums_name(session):
    text_request = text(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='atomlabreguser'")
    result = await session.execute(text_request)
    data = [row._asdict() for row in result]

    new_data = []
    for row in data:
        value = list(row.values())
        new_data.append(*value)
    return new_data
