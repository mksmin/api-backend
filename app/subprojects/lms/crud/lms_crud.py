from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from subprojects.lms.crud.services.lms_flows import LMSFlowsService
from subprojects.lms.crud.services.projects import ProjectService


class LMSCRUDService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.lms_flows: LMSFlowsService = LMSFlowsService(session)
        self.projects: ProjectService = ProjectService(session)


async def get_lms_crud_service(
    session: Annotated[
        AsyncSession,
        Depends(
            db_helper.session_getter,
        ),
    ],
) -> LMSCRUDService:
    return LMSCRUDService(session)


GetLMSCRUDService = Annotated[
    LMSCRUDService,
    Depends(get_lms_crud_service),
]
