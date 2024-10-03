"""
Module with functions for database operations
"""

# import from libraries
from functools import wraps
from sqlalchemy.sql import text

# import from modules
from app.database.models import async_session


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

    # str_namecolum = ''
    # str_valuecolum = ''
    # for key in values.keys():
    #     str_namecolum += f"{key.lower()}, "
    #     str_valuecolum += f"'{str(values[key]['value'])}', "

    list_namecolums = list()
    list_valuecolums = list()
    for key in values.keys():
        value = values[key]['value']
        list_namecolums.append(key.lower())
        list_valuecolums.append(value)
    str_namecolum = ', '.join(list_namecolums)
    str_valuecolum = ', '.join(list_valuecolums)

    text_of_query = text(f'INSERT INTO {name_db} ({str_namecolum}) VALUES ({str_valuecolum})')
    await session.execute(text_of_query)
    await session.commit()


@connection
async def add_column_for_db(session,
                            columns_names: set,
                            name_db: str,
                            type_colums: dict) -> None:
    """
    Функция автоматического добавления столбцов в таблице,
    если изначально не можем создать таблицу до получения запроса
    :param session:
    :param columns_names: названия столбцов. Example: secondname
    :param name_db: имя таблицы в которую будем сохранять
    :param type_colums: тип данных, который хранит столбец
    :return: None
    """
    sql_types = {
        'str': 'VARCHAR(250)',
        'int': 'int',
        'date': 'date'
    }

    for col in columns_names:
        type_col = type_colums[col]['type']
        text_table = text(f'ALTER TABLE {name_db} ADD {col} {sql_types[type_col]}')
        await session.execute(text_table)
    await session.commit()


@connection
async def get_colums_name(session, name_of_db: str) -> list:
    """
    Функция для получения существующих имен столбцов в таблице
    :param session:
    :param name_of_db: Имя таблицы из базы данных
    :return: list with names of colums. Example: ['firstname', 'secondname']
    """
    text_request = text(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{name_of_db}'")
    result = await session.execute(text_request)
    data = [columnname._asdict() for columnname in result]

    new_data = []
    for col in data:
        value = list(col.values())
        new_data.append(*value)
    return new_data


@connection
async def get_registration_stat(session, name_db: str) -> dict:
    text_request_detail = text(f'SELECT competention, count(*) '
                               f'FROM {name_db}'
                               f'GROUP BY competention'
                               f'ORDER BY competention')
    text_request_general = text(f'SELECT count(*) FROM {name_db}')

    result_detail = await session.execute(text_request_detail)
    result_general = await session.execute(text_request_general)

    # TODO: преобразовать полученный результат с db в Dict
    # TODO: убрав тем самым переработку ответа с функции get_statistics() в get_endpoints.py
    # total_bids = result_general.fetchall() # WIP
    # result_dict = {"total_users": total_bids, "details": {}} # WIP

    data = [competention._asdict() for competention in result_detail]
    return result_general.fetchall(), data
