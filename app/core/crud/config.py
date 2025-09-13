from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from typing import (
    Any,
    Concatenate,
    ParamSpec,
    TypeVar,
)

from sqlalchemy.ext.asyncio import AsyncSession

from core import db_helper

# Типы
P = ParamSpec("P")
R = TypeVar("R")


def connector(
    function: Callable[Concatenate[AsyncSession, P], Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    @wraps(function)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        async with db_helper.session_factory() as session:
            return await function(session, *args, **kwargs)

    return wrapper
