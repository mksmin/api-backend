from fastapi import (
    APIRouter,
    Header,
    Body,
    File,
    Request,
    HTTPException,
    status,
    Query,
    Depends,
)
from pydantic import BaseModel
from sqlalchemy import select

from .auth import token_utils
from app.core import crud_manager, settings, db_helper
from app.core.database.schemas import ProjectResponseSchema
from ...core.database import Project, User

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


@router.get(
    "/owner",
    include_in_schema=settings.run.dev_mode,
)
async def get_projects_owner(
    request: Request, user: str | bool = Depends(token_utils.check_access_token)
):
    payload = await token_utils.decode_jwt(user)
    user_id: str = payload.get("user_id")

    async with db_helper.session_factory() as session:
        stmt = (
            select(Project)
            .join(User, Project.prj_owner == User.id)
            .where(User.id == int(user_id), Project.deleted_at.is_(None))
        )
        results = await session.execute(stmt)
        projects: Project = results.scalars().all()
        return {"projects": [{"id": p.id, "name": p.prj_name} for p in projects]}
