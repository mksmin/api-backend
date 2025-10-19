from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.services import UserService
from core.database.db_helper import db_helper


class CRUDService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.user: UserService = UserService(session)


async def get_crud_service(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> CRUDService:
    yield CRUDService(session)


GetCRUDService = Annotated[
    CRUDService,
    Depends(get_crud_service),
]
