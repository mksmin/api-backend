from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import LMSFlow
from schemas.lms_flows import LMSFlowsCreateModel


class LMSFlowManager:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_all(
        self,
        project_id: int,
    ) -> Sequence[LMSFlow]:
        stmt = (
            select(
                LMSFlow,
            )
            .where(
                LMSFlow.project_id == project_id,
                LMSFlow.deleted_at.is_(None),
            )
            .order_by(
                LMSFlow.id,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_uuid(
        self,
        project_id: int,
        flow_uuid: UUID,
    ) -> LMSFlow | None:
        stmt = select(
            LMSFlow,
        ).where(
            LMSFlow.project_id == project_id,
            LMSFlow.uuid == flow_uuid,
            LMSFlow.deleted_at.is_(None),
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        flow_in: LMSFlowsCreateModel,
    ) -> LMSFlow:
        flow = LMSFlow(**flow_in.model_dump())
        self.session.add(flow)
        return flow

    async def update_title(
        self,
        project_id: int,
        flow_uuid: UUID,
        title: str,
    ) -> LMSFlow | None:
        stmt = (
            update(
                LMSFlow,
            )
            .where(
                LMSFlow.project_id == project_id,
                LMSFlow.uuid == flow_uuid,
                LMSFlow.deleted_at.is_(None),
            )
            .values(
                title=title,
            )
            .returning(
                LMSFlow,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_project(
        self,
        project_id: int,
    ) -> int:
        stmt = select(
            func.count(LMSFlow.id),
        ).where(
            LMSFlow.project_id == project_id,
            LMSFlow.deleted_at.is_(None),
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()
