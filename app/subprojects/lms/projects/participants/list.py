from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.params import Form
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from starlette.responses import RedirectResponse

from app_exceptions import ProjectNotFoundError
from app_exceptions import UserNotFoundError
from app_exceptions.exceptions import EnrollmentAlreadyExistsError
from app_exceptions.exceptions import EnrollmentRestoreRequiredError
from app_exceptions.exceptions import ParticipantCreationConflictError
from app_exceptions.exceptions import ParticipantUnavailableError
from auth import jwt_helper
from auth.csrf_helper import csrf_token_for
from auth.csrf_helper import require_csrf_token
from paths_constants import templates
from schemas import ProjectSchema
from schemas.lms.enrollments import LMSEnrollmentsCreateSchema
from subprojects.lms.constraints import PARTICIPANTS_TEMPLATE_PATH
from subprojects.lms.crud import GetLMSCRUDService
from subprojects.lms.crud.lms_crud import LMSCRUDService
from subprojects.lms.crud.services.lms_flows import FlowNotFoundError
from subprojects.lms.projects.flows.list import OwnedProject

router = APIRouter()


def get_participant_form(
    full_name: Annotated[str, Form()] = "",
    email: Annotated[str, Form()] = "",
    flow_uuid: Annotated[str, Form()] = "",
) -> dict[str, str]:
    return {
        "full_name": full_name,
        "email": email,
        "flow_uuid": flow_uuid,
    }


async def render_participants_page(
    request: Request,
    project: ProjectSchema,
    lms_crud_service: LMSCRUDService,
    *,
    participant_form: dict[str, str] | None = None,
    error: str | None = None,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    claims = await jwt_helper.decode_jwt(access_token)
    user_id = int(claims["user_id"])

    enrollments = await lms_crud_service.enrollments.get_all(
        project_id=project.id,
        user_id=user_id,
    )
    flows = await lms_crud_service.lms_flows.get_all(
        project_id=project.id,
        user_id=user_id,
    )

    context = {
        "project_section": "participants",
        "csrf_token": csrf_token_for(
            claims["jti"],
        ),
        "can_manage_participants": True,
        "project": project,
        "enrollments": enrollments,
        "flows": flows,
        "enroll_url": request.url_for(
            "lms-participants:create:submit",
            project_uuid=project.uuid,
        ),
        "participant_form": participant_form or {},
        "participant_error": error,
    }

    return templates.TemplateResponse(
        request=request,
        name=f"{PARTICIPANTS_TEMPLATE_PATH}/list.html",
        context=context,
        status_code=status_code,
    )


@router.get(
    "/",
    name="lms-participants:list",
)
async def get_participants_list_page(
    request: Request,
    project: OwnedProject,
    lms_crud_service: GetLMSCRUDService,
) -> HTMLResponse:

    return await render_participants_page(
        request=request,
        project=project,
        lms_crud_service=lms_crud_service,
    )


@router.post(
    "/",
    name="lms-participants:create:submit",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
)
async def create_participants_page(
    request: Request,
    project: OwnedProject,
    lms_crud_service: GetLMSCRUDService,
    user_id: Annotated[
        int,
        Depends(
            require_csrf_token,
        ),
    ],
    participant_form: Annotated[
        dict[str, str],
        Depends(get_participant_form),
    ],
) -> HTMLResponse | RedirectResponse:
    try:
        enrolment_in = LMSEnrollmentsCreateSchema.model_validate(
            participant_form,
        )
    except ValidationError:
        return await render_participants_page(
            request=request,
            project=project,
            lms_crud_service=lms_crud_service,
            participant_form=participant_form,
            error="Проверь ФИО, email и выбранный поток",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )

    try:
        await lms_crud_service.enrollments.create_enrollment(
            project_id=project.id,
            enrollment_in=enrolment_in,
            user_id=user_id,
        )
    except (
        ProjectNotFoundError,
        UserNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден или недоступен.",
        ) from exc
    except (
        EnrollmentAlreadyExistsError,
        EnrollmentRestoreRequiredError,
        ParticipantCreationConflictError,
        ParticipantUnavailableError,
        FlowNotFoundError,
    ) as exc:
        messages = {
            EnrollmentAlreadyExistsError: "Слушатель уже зачислен в этот проект.",
            EnrollmentRestoreRequiredError: (
                "Слушатель исключён. Требуется восстановление зачисления."
            ),
            ParticipantCreationConflictError: (
                "Слушатель был создан другим запросом. Повтори зачисление."
            ),
            ParticipantUnavailableError: (
                "Запись слушателя удалена и недоступна для зачисления."
            ),
            FlowNotFoundError: "Выбранный поток недоступен. Выбери другой поток.",
        }

        return await render_participants_page(
            request=request,
            project=project,
            lms_crud_service=lms_crud_service,
            participant_form=participant_form,
            error=messages[type(exc)],
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse(
        url=request.url_for(
            "lms-participants:list",
            project_uuid=project.uuid,
        ),
        status_code=status.HTTP_303_SEE_OTHER,
    )
