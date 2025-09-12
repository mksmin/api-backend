from functools import wraps
from typing import Callable

from core import db_helper


def connector(function: Callable) -> Callable:
    @wraps(function)
    async def wrapper(*args, **kwargs):
        async with db_helper.session_factory() as session:
            return await function(session, *args, **kwargs)

    return wrapper
