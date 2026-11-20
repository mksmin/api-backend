from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from pydantic import ValidationError

from app_exceptions import ProjectAlreadyExistsError
from app_exceptions import UserNotFoundError
from app_exceptions.exceptions import ProjectCreationForbiddenError
from auth import jwt_helper
from auth.csrf_helper import csrf_token_for
from auth.csrf_helper import require_csrf_token
from config import settings
from core.crud import GetCRUDService
from paths_constants import templates
from schemas import ProjectCreateSchema
from schemas.projects import DESCRIPTION_MAX_LENGTH
from schemas.projects import TITLE_MAX_LENGTH
from subprojects.lms.constraints import LMS_TEMPLATE_PATH

router = APIRouter(
    prefix="/new",
)

TEMPLATE_NAME = LMS_TEMPLATE_PATH + "/projects" + "/create.html"


def require_organizer(
    user_id: int | str,
) -> None:
    if not settings.lms.can_create_project(
        user_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )


async def render_create_form(
    request: Request,
    *,
    title: str = "",
    description: str = "",
    errors: dict[str, list[str]] | None = None,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    claims = await jwt_helper.decode_jwt(access_token)
    return templates.TemplateResponse(
        request=request,
        name=TEMPLATE_NAME,
        context={
            "csrf_token": csrf_token_for(claims["jti"]),
            "form": {
                "title": title,
                "description": description,
            },
            "errors": errors or {},
            "title_max_length": TITLE_MAX_LENGTH,
            "description_max_length": DESCRIPTION_MAX_LENGTH,
        },
        status_code=status_code,
    )


@router.get(
    "",
    name="lms-project:create",
    include_in_schema=settings.run.dev_mode,
)
async def get_page_project_create(
    request: Request,
    user_id: Annotated[
        str,
        Depends(jwt_helper.strict_validate_access_token),
    ],
) -> HTMLResponse:
    require_organizer(user_id)
    return await render_create_form(request)


class ProjectCreateFormSchema(BaseModel):
    title: str = ""
    description: str = ""


@router.post(
    "",
    name="lms-projects:create:submit",
    include_in_schema=settings.run.dev_mode,
    response_model=None,
)
async def form_create_project(
    request: Request,
    crud_service: GetCRUDService,
    user_id: Annotated[
        int,
        Depends(require_csrf_token),
    ],
    form_data: Annotated[
        ProjectCreateFormSchema,
        Form(),
    ],
) -> RedirectResponse | HTMLResponse:
    require_organizer(user_id)

    try:
        project_in = ProjectCreateSchema.model_validate(form_data)
    except ValidationError as exc:
        messages = {
            "missing": "Заполни это поле.",
            "string_too_short": "Введи название проекта.",
            "string_too_long": "Максимум {max_length} символов.",
            "string_type": "Введи текст.",
        }
        errors: dict[str, list[str]] = {}

        for issue in exc.errors(include_input=False):
            loc = issue["loc"]
            field = loc[0] if loc and isinstance(loc[0], str) else "_form"
            if field not in ("title", "description"):
                field = "_form"

            message = messages.get(issue["type"], "Проверь введённые данные.")
            message = message.format(**issue.get("ctx", {}))

            errors.setdefault(field, []).append(message)

        return await render_create_form(
            request,
            title=form_data.title,
            description=form_data.description,
            errors=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )

    try:
        await crud_service.project.create_project(
            project_create=project_in,
            user_id=user_id,
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e
    except ProjectAlreadyExistsError:
        return await render_create_form(
            request,
            title=form_data.title,
            description=form_data.description,
            errors={"title": ["Проект с таким названием уже существует."]},
            status_code=status.HTTP_409_CONFLICT,
        )
    except ProjectCreationForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        ) from e
    else:
        return RedirectResponse(
            status_code=status.HTTP_303_SEE_OTHER,
            url=request.url_for("lms:index-page"),
        )
