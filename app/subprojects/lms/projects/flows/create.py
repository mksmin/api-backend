from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app_exceptions import ProjectNotFoundError
from app_exceptions import UserNotFoundError
from auth import jwt_helper
from auth.csrf_helper import csrf_token_for
from auth.csrf_helper import require_csrf_token
from config import settings
from paths_constants import templates
from schemas.lms.flows import LMSFlowsCreateSchema
from subprojects.lms.constraints import FLOWS_TEMPLATE_PATH
from subprojects.lms.crud import GetLMSCRUDService
from subprojects.lms.crud.services.lms_flows import FlowAlreadyExistsError
from subprojects.lms.projects.flows.list import OwnedProject

TEMPLATE_PATH = FLOWS_TEMPLATE_PATH + "/create.html"
router = APIRouter()


async def render_flow_create_page(
    request: Request,
    *,
    title: str = "",
    errors: (
        dict[
            str,
            list[str],
        ]
        | None
    ) = None,
    extra_context: (
        dict[
            str,
            Any,
        ]
        | None
    ) = None,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    claims = await jwt_helper.decode_jwt(
        access_token,
    )

    context = {
        "csrf_token": csrf_token_for(
            claims["jti"],
        ),
        "form": {
            "title": title,
        },
        "errors": errors or {},
    }
    if extra_context:
        context.update(extra_context)

    return templates.TemplateResponse(
        request=request,
        name=TEMPLATE_PATH,
        context=context,
        status_code=status_code,
    )


@router.get(
    "/new",
    name="lms-flow:create",
    include_in_schema=settings.run.dev_mode,
)
async def get_page_create_flow(
    request: Request,
    project: OwnedProject,
) -> HTMLResponse:
    context = {
        "project": project,
        "project_section": "flows",
    }
    return await render_flow_create_page(
        request,
        extra_context=context,
    )


@router.post(
    "/new",
    name="lms-flow:create:submit",
    include_in_schema=settings.run.dev_mode,
    response_model=None,
)
async def create_flow(
    request: Request,
    project: OwnedProject,
    lms_crud_service: GetLMSCRUDService,
    user_id: Annotated[
        int,
        Depends(
            require_csrf_token,
        ),
    ],
    flow_title: Annotated[
        str,
        Form(),
    ] = "",
) -> RedirectResponse | HTMLResponse:
    context = {
        "project": project,
        "project_section": "flows",
    }

    try:
        flow_in = LMSFlowsCreateSchema(
            title=flow_title,
        )
    except ValidationError as exc:
        messages = {
            "missing": "Заполни это поле.",
            "string_too_short": "Введи название потока.",
            "string_too_long": "Максимум {max_length} символов.",
            "string_type": "Введи текст.",
        }
        errors: dict[str, list[str]] = {}

        for issue in exc.errors(
            include_input=False,
        ):
            loc = issue["loc"]
            field = loc[0] if loc and isinstance(loc[0], str) else "_form"
            if field != "title":
                field = "_form"

            message = messages.get(
                issue["type"],
                "Проверь введённые данные.",
            )
            message = message.format(
                **issue.get(
                    "ctx",
                    {},
                ),
            )

            errors.setdefault(
                field,
                [],
            ).append(
                message,
            )

        return await render_flow_create_page(
            request=request,
            title=flow_title,
            errors=errors,
            extra_context=context,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )

    try:
        await lms_crud_service.lms_flows.create_flow(
            project_id=project.id,
            flow_in=flow_in,
            user_id=user_id,
        )
    except FlowAlreadyExistsError:
        return await render_flow_create_page(
            request=request,
            title=flow_title,
            errors={
                "title": ["Поток с таким названием уже существует."],
            },
            extra_context=context,
            status_code=status.HTTP_409_CONFLICT,
        )
    except (
        ProjectNotFoundError,
        UserNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден или у вас нет к нему доступа.",
        ) from exc
    else:
        return RedirectResponse(
            status_code=status.HTTP_303_SEE_OTHER,
            url=request.url_for(
                "lms-flows:list",
                project_uuid=project.uuid,
            ),
        )
