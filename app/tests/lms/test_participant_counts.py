from datetime import UTC
from datetime import datetime

import pytest
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app_exceptions import ProjectNotFoundError
from core.database import Project
from core.database.lms import LMSEnrollment
from core.database.lms import LMSFlow
from core.database.lms import LMSParticipant
from schemas import ProjectSchema
from schemas.lms.enrollments import LMSEnrollmentsCreateSchema
from schemas.lms.flows import LMSFlowsReadSchema
from subprojects.lms.crud.services.enrollments import LMSEnrollmentsService

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "hidden_record",
    ["excluded", "enrollment", "participant"],
)
async def test_counts_exclude_inactive_or_deleted_records(
    db_session: AsyncSession,
    project: ProjectSchema,
    flow: LMSFlowsReadSchema,
    owner_id: int,
    hidden_record: str,
) -> None:
    service = LMSEnrollmentsService(db_session)
    enrollments = [
        await service.create_enrollment(
            project_id=project.id,
            enrollment_in=LMSEnrollmentsCreateSchema(
                full_name=name,
                email=f"{name}@example.com",
                flow_uuid=flow.uuid,
            ),
            user_id=owner_id,
        )
        for name in ("visible", "hidden")
    ]

    expected_count = len(enrollments)
    assert (
        await service.count_by_project(project.id, user_id=owner_id) == expected_count
    )
    assert await service.count_by_owned_projects(user_id=owner_id) == {
        project.uuid: len(enrollments),
    }

    hidden = enrollments[1]
    deleted_at = datetime.now(UTC).replace(tzinfo=None)
    if hidden_record == "excluded":
        stmt = (
            update(LMSEnrollment)
            .where(LMSEnrollment.id == hidden.id)
            .values(status="excluded")
        )
    elif hidden_record == "enrollment":
        stmt = (
            update(LMSEnrollment)
            .where(LMSEnrollment.id == hidden.id)
            .values(deleted_at=deleted_at)
        )
    else:
        stmt = (
            update(LMSParticipant)
            .where(LMSParticipant.uuid == hidden.participant_uuid)
            .values(deleted_at=deleted_at)
        )
    await db_session.execute(stmt)
    await db_session.commit()

    assert await service.count_by_project(project.id, user_id=owner_id) == 1
    assert await service.count_by_owned_projects(user_id=owner_id) == {
        project.uuid: 1,
    }
    participants = await service.get_all(
        project.id,
        user_id=owner_id,
        flow_uuid=flow.uuid,
        active_only=True,
    )
    assert [participant.uuid for participant in participants] == [enrollments[0].uuid]


async def test_counts_are_scoped_to_owner_project_and_flow(
    db_session: AsyncSession,
    project: ProjectSchema,
    flow: LMSFlowsReadSchema,
    owner_id: int,
    outsider_id: int,
) -> None:
    service = LMSEnrollmentsService(db_session)
    other_project = Project(title="Other owned project", owner_id=owner_id)
    foreign_project = Project(title="Foreign project", owner_id=outsider_id)
    db_session.add_all([other_project, foreign_project])
    await db_session.flush()
    other_flow = LMSFlow(project_id=other_project.id, title="Other flow")
    foreign_flow = LMSFlow(project_id=foreign_project.id, title="Foreign flow")
    second_flow = LMSFlow(project_id=project.id, title="Second flow")
    db_session.add_all([other_flow, foreign_flow, second_flow])
    await db_session.commit()

    first = await service.create_enrollment(
        project.id,
        LMSEnrollmentsCreateSchema(
            full_name="Shared participant",
            email="shared@example.com",
            flow_uuid=flow.uuid,
        ),
        user_id=owner_id,
    )
    for target_project, target_flow, user_id in (
        (other_project, other_flow, owner_id),
        (foreign_project, foreign_flow, outsider_id),
    ):
        result = await service.create_enrollment(
            target_project.id,
            LMSEnrollmentsCreateSchema(
                full_name="Shared participant",
                email="SHARED@example.com",
                flow_uuid=target_flow.uuid,
            ),
            user_id=user_id,
        )
        assert result.participant_uuid == first.participant_uuid

    await service.create_enrollment(
        project.id,
        LMSEnrollmentsCreateSchema(
            full_name="Second flow participant",
            email="second-flow@example.com",
            flow_uuid=second_flow.uuid,
        ),
        user_id=owner_id,
    )

    expected_project_count = 2
    assert (
        await service.count_by_project(project.id, user_id=owner_id)
        == expected_project_count
    )
    assert await service.count_by_owned_projects(user_id=owner_id) == {
        project.uuid: expected_project_count,
        other_project.uuid: 1,
    }
    assert await service.count_by_owned_projects(user_id=outsider_id) == {
        foreign_project.uuid: 1,
    }
    participants = await service.get_all(
        project.id,
        user_id=owner_id,
        flow_uuid=flow.uuid,
        active_only=True,
    )
    assert [participant.uuid for participant in participants] == [first.uuid]


async def test_empty_project_count_and_access(
    db_session: AsyncSession,
    project: ProjectSchema,
    owner_id: int,
    outsider_id: int,
) -> None:
    service = LMSEnrollmentsService(db_session)

    assert await service.count_by_project(project.id, user_id=owner_id) == 0
    assert await service.count_by_owned_projects(user_id=owner_id) == {}

    with pytest.raises(ProjectNotFoundError):
        await service.count_by_project(project.id, user_id=outsider_id)
