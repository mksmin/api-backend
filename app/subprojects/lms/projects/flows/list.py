from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse

from app_exceptions import InvalidUUIDError
from app_exceptions import ProjectNotFoundError
from app_exceptions import UserNotFoundError
from auth import jwt_helper
from paths_constants import templates
from schemas import ProjectSchema
from subprojects.lms.constraints import FLOWS_TEMPLATE_PATH
from subprojects.lms.crud import GetLMSCRUDService

router = APIRouter()


async def get_owned_project(
    lms_crud_service: GetLMSCRUDService,
    project_uuid: str,
    user_id: Annotated[
        int,
        Depends(
            jwt_helper.soft_validate_access_token,
        ),
    ],
) -> ProjectSchema:
    try:
        return await lms_crud_service.projects.get_by_uuid(
            user_id=user_id,
            project_uuid=project_uuid,
        )
    except (
        InvalidUUIDError,
        ProjectNotFoundError,
        UserNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc


OwnedProject = Annotated[
    ProjectSchema,
    Depends(get_owned_project),
]


@router.get(
    "/",
    name="lms-flows:list",
)
async def get_flows_list_page(
    request: Request,
    lms_crud_service: GetLMSCRUDService,
    user_id: Annotated[
        int,
        Depends(
            jwt_helper.soft_validate_access_token,
        ),
    ],
    project: OwnedProject,
) -> HTMLResponse:

    flows = await lms_crud_service.lms_flows.get_all(
        user_id=user_id,
        project_id=project.id,
    )

    return templates.TemplateResponse(
        request=request,
        name=f"{FLOWS_TEMPLATE_PATH}/list.html",
        context={
            "project": project,
            "project_section": "flows",
            "flows": flows,
            "can_manage_flows": True,
        },
    )
