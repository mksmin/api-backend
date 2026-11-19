from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app_exceptions import InvalidUUIDError
from auth import jwt_helper
from config import settings
from core.crud import GetCRUDService
from core.crud.services.lms_flows import FlowNotFoundError
from paths_constants import templates
from schemas.lms_flows import LMSFlowsReadSchema
from subprojects.lms.constraints import LMS_TEMPLATE_PATH
from subprojects.lms.projects.flows.list import OwnedProject

router = APIRouter()


async def get_flow_by_uuid(
    flow_uuid: str,
    user_id: Annotated[
        str,
        Depends(jwt_helper.strict_validate_access_token),
    ],
    crud_service: GetCRUDService,
    project: OwnedProject,
) -> LMSFlowsReadSchema:
    try:
        flow = await crud_service.lms_flow.get_by_uuid(
            flow_uuid=flow_uuid,
            project_id=project.id,
            user_id=int(user_id),
        )
    except (
        FlowNotFoundError,
        InvalidUUIDError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow not found",
        ) from e
    else:
        return flow


@router.get(
    "/{flow_uuid}",
    name="lms-flow:details",
    include_in_schema=settings.run.dev_mode,
)
async def get_page_flow_details(
    request: Request,
    flow: Annotated[
        LMSFlowsReadSchema,
        Depends(get_flow_by_uuid),
    ],
    project: OwnedProject,
) -> HTMLResponse:
    participants = [
        {
            "full_name": "Минин Максим Алексеевич",
            "email": "mininname@vk.com",
        },
    ]
    return templates.TemplateResponse(
        request=request,
        name=f"{LMS_TEMPLATE_PATH}/projects/flows/details.html",
        context={
            "project": project,
            "flow": flow,
            "project_section": "flows",
            "participants": participants,
        },
    )
