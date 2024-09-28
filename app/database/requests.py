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
async def set_user_registration(session, values: dict, name_db: str) -> None:
    str_namecolum = ''
    str_valuecolum = ''
    for key in values.keys():
        str_namecolum += f"{key.lower()}, "
        str_valuecolum += f"'{str(values[key]['value'])}', "

    text_table = text(f'INSERT INTO {name_db} ({str_namecolum[:-2]}) VALUES ({str_valuecolum[:-2]})')
    await session.execute(text_table)
    await session.commit()


@connection
async def add_column_for_db(session,
                            colums_names: set, name_db: str,
                            type_colums: dict):
    sql_types = {
        'str': 'VARCHAR(250)',
        'int': 'int',
        'date': 'date'
    }

    for col in colums_names:
        type_col = type_colums[col]['type']
        text_table = text(f'ALTER TABLE {name_db} ADD {col} {sql_types[type_col]}')
        await session.execute(text_table)
    await session.commit()


@connection
async def get_colums_name(session, name_of_db: str):
    text_request = text(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{name_of_db}'")
    result = await session.execute(text_request)
    data = [row._asdict() for row in result]

    new_data = []
    for row in data:
        value = list(row.values())
        new_data.append(*value)
    return new_data
