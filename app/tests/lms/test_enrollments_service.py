import pytest
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app_exceptions.exceptions import EnrollmentAlreadyExistsError
from core.database.lms import LMSEnrollment
from core.database.lms import LMSParticipant
from schemas import ProjectSchema
from schemas.lms.enrollments import LMSEnrollmentsCreateModel
from schemas.lms.enrollments import LMSEnrollmentsCreateSchema
from schemas.lms.flows import LMSFlowsReadSchema
from subprojects.lms.crud.services.enrollments import LMSEnrollmentsService

pytestmark = pytest.mark.asyncio


class EnrollmentWriteError(Exception): ...


async def test_create_enrollment_creates_participant(
    db_session: AsyncSession,
    project: ProjectSchema,
    flow: LMSFlowsReadSchema,
    owner_id: int,
) -> None:
    service = LMSEnrollmentsService(db_session)
    enrollment_in = LMSEnrollmentsCreateSchema(
        full_name="Test Testov",
        email="test@example.com",
        flow_uuid=flow.uuid,
    )
    result = await service.create_enrollment(
        project_id=project.id,
        enrollment_in=enrollment_in,
        user_id=owner_id,
    )

    participant = await db_session.scalar(
        select(
            LMSParticipant,
        ).where(
            LMSParticipant.uuid == result.participant_uuid,
        ),
    )
    enrollment = await db_session.scalar(
        select(
            LMSEnrollment,
        ).where(
            LMSEnrollment.uuid == result.uuid,
        ),
    )

    assert participant is not None
    assert participant.full_name == "Test Testov"
    assert participant.email == "test@example.com"

    assert enrollment is not None
    assert enrollment.participant_id == participant.id
    assert enrollment.project_id == project.id
    assert enrollment.flow_id == flow.id
    assert enrollment.status == "active"

    assert result.project_uuid == project.uuid
    assert result.flow_uuid == flow.uuid


async def test_duplicate_enrollment_preserves_original_participant(
    db_session: AsyncSession,
    project: ProjectSchema,
    flow: LMSFlowsReadSchema,
    owner_id: int,
) -> None:
    service = LMSEnrollmentsService(db_session)

    first_enrollment_in = LMSEnrollmentsCreateSchema(
        full_name="Test Testov",
        email="test@example.com",
        flow_uuid=flow.uuid,
    )

    first = await service.create_enrollment(
        project_id=project.id,
        enrollment_in=first_enrollment_in,
        user_id=owner_id,
    )

    second_enrollment_in = LMSEnrollmentsCreateSchema(
        full_name="Test Testov 2",
        email=" TEST@example.com ",
        flow_uuid=flow.uuid,
    )
    with pytest.raises(
        EnrollmentAlreadyExistsError,
    ):
        await service.create_enrollment(
            project_id=project.id,
            enrollment_in=second_enrollment_in,
            user_id=owner_id,
        )

    participants_count = await db_session.scalar(
        select(func.count())
        .select_from(LMSParticipant)
        .where(
            LMSParticipant.email == "test@example.com",
        ),
    )
    enrollments_count = await db_session.scalar(
        select(func.count())
        .select_from(LMSEnrollment)
        .where(
            LMSEnrollment.project_id == project.id,
        ),
    )
    saved_name = await db_session.scalar(
        select(LMSParticipant.full_name).where(
            LMSParticipant.uuid == first.participant_uuid,
        ),
    )

    assert participants_count == 1
    assert enrollments_count == 1
    assert saved_name == "Test Testov"


async def test_different_emails_create_independent_enrollments(
    db_session: AsyncSession,
    project: ProjectSchema,
    flow: LMSFlowsReadSchema,
    owner_id: int,
) -> None:
    service = LMSEnrollmentsService(db_session)

    first = await service.create_enrollment(
        project_id=project.id,
        enrollment_in=LMSEnrollmentsCreateSchema(
            full_name="Test Testov",
            email="test@example.com",
            flow_uuid=flow.uuid,
        ),
        user_id=owner_id,
    )
    second = await service.create_enrollment(
        project_id=project.id,
        enrollment_in=LMSEnrollmentsCreateSchema(
            full_name="Test Testov",
            email="test2@example.com",
            flow_uuid=flow.uuid,
        ),
        user_id=owner_id,
    )

    assert first.uuid != second.uuid
    assert first.participant_uuid != second.participant_uuid

    emails = await db_session.scalars(
        select(LMSParticipant.email)
        .join(
            LMSEnrollment,
            LMSEnrollment.participant_id == LMSParticipant.id,
        )
        .where(
            LMSEnrollment.project_id == project.id,
        ),
    )

    assert sorted(emails.all()) == ["test2@example.com", "test@example.com"]


async def test_enrollment_failure_rolls_back_participant_and_allows_retry(
    db_session: AsyncSession,
    project: ProjectSchema,
    flow: LMSFlowsReadSchema,
    owner_id: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LMSEnrollmentsService(db_session)
    enrollment_in = LMSEnrollmentsCreateSchema(
        full_name="Test Testov",
        email="test@example.com",
        flow_uuid=flow.uuid,
    )
    original_create = service.manager.create

    async def fail_after_insert(
        enrolment_in: LMSEnrollmentsCreateModel,
    ) -> LMSEnrollment:
        await original_create(enrolment_in)
        await db_session.flush()
        raise EnrollmentWriteError

    with monkeypatch.context() as patch:
        patch.setattr(service.manager, "create", fail_after_insert)

        with pytest.raises(EnrollmentWriteError):
            await service.create_enrollment(
                project_id=project.id,
                enrollment_in=enrollment_in,
                user_id=owner_id,
            )

    participant_id = await db_session.scalar(
        select(LMSParticipant.id).where(
            LMSParticipant.email == "test@example.com",
        ),
    )
    enrollment_id = await db_session.scalar(
        select(LMSEnrollment.id).where(
            LMSEnrollment.project_id == project.id,
        ),
    )

    assert participant_id is None
    assert enrollment_id is None

    result = await service.create_enrollment(
        project_id=project.id,
        enrollment_in=enrollment_in,
        user_id=owner_id,
    )

    saved_enrollment_id = await db_session.scalar(
        select(LMSEnrollment.id).where(
            LMSEnrollment.uuid == result.uuid,
        ),
    )

    assert saved_enrollment_id == result.id
