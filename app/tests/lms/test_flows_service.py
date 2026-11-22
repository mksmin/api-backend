import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import LMSFlow
from schemas import ProjectSchema
from schemas.lms_flows import LMSFlowsCreateSchema
from schemas.lms_flows import LMSFlowsReadSchema
from schemas.lms_flows import LMSFlowsUpdateSchema
from subprojects.lms.crud.services import LMSFlowsService
from subprojects.lms.crud.services.lms_flows import FlowAlreadyExistsError

pytestmark = pytest.mark.asyncio


async def test_duplicate_title_rolls_back_and_allows_retry(
    db_session: AsyncSession,
    flows_service: LMSFlowsService,
    project: ProjectSchema,
    flow: LMSFlowsReadSchema,
    owner_id: int,
) -> None:
    await flows_service.create_flow(
        project_id=project.id,
        user_id=owner_id,
        flow_in=LMSFlowsCreateSchema(
            title="Analytics",
        ),
    )

    with pytest.raises(
        FlowAlreadyExistsError,
    ):
        await flows_service.update_title(
            project_id=project.id,
            flow_uuid=flow.uuid,
            flow_in=LMSFlowsUpdateSchema(
                title="   ANALYTICS   ",
            ),
            user_id=owner_id,
        )

    saved_title = await db_session.scalar(
        select(
            LMSFlow.title,
        ).where(
            LMSFlow.uuid == flow.uuid,
        ),
    )

    assert saved_title == "Test Flow"

    updated = await flows_service.update_title(
        project_id=project.id,
        flow_uuid=flow.uuid,
        flow_in=LMSFlowsUpdateSchema(
            title="  Backend   ",
        ),
        user_id=owner_id,
    )

    assert updated.uuid == flow.uuid
    assert updated.title == "Backend"

    saved_title = await db_session.scalar(
        select(
            LMSFlow.title,
        ).where(
            LMSFlow.uuid == flow.uuid,
        ),
    )

    assert saved_title == "Backend"
