from fastapi import (
    APIRouter,
    Header,
    Body,
    File,
    UploadFile,
    HTTPException,
    status,
    Query,
    Depends,
)
from pydantic import BaseModel

from app.core import crud_manager, settings
from app.core.database.schemas import ProjectResponseSchema

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


# Схема для параметров запроса
class ProjectFilter(BaseModel):
    owner_id: int
    project_id: int | None
    limit: int | None
    offset: int | None

    @classmethod
    def from_query(
        cls,
        owner_id: int = Query(..., description="tg_id пользователя", alias="prj_owner"),
        project_id: int | None = Query(None, description="id проекта", alias="prj_id"),
        limit: int | None = Query(None, description="Лимит"),
        offset: int | None = Query(None, description="Смещение"),
    ):

        return cls(
            owner_id=owner_id,
            project_id=project_id,
            limit=limit,
            offset=offset,
        )


@router.get(
    "",
    include_in_schema=settings.run.dev_mode,
    response_model=dict[int, ProjectResponseSchema],
)
async def get_projects(
    prj_filter: ProjectFilter = Depends(ProjectFilter.from_query),
):

    try:
        if prj_filter.project_id:
            projects = await crud_manager.project.get_project_by_id(
                prj_filter.owner_id, prj_filter.project_id
            )
        else:
            projects = await crud_manager.project.get_all(prj_filter.owner_id)
        return {
            i: ProjectResponseSchema.model_validate(item)
            for i, item in enumerate(projects)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
        )
