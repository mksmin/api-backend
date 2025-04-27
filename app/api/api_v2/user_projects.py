# import from lib
from datetime import datetime
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
    Response,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from uuid import UUID

# import from modules
from .auth import token_utils
from app.core import crud_manager, settings, db_helper
from app.core.database import Project, User
from app.core.database.schemas import ProjectResponseSchema
from app.core.database.schemas import project as ProjectSchemas


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
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
    """

    :param prj_filter:
    :return:
    """

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
    summary="Get projects by owner",
    include_in_schema=settings.run.dev_mode,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "model": list[ProjectSchemas.ProjectResponseSchema],
            "description": "Список проектов пользователя",
        },
        401: {
            "model": ProjectSchemas.BaseMessageResponse,
        },
    },
)
async def get_projects_owner(
    user: str | bool = Depends(token_utils.check_access_token),
):
    """
    Возвращает список проектов, принадлежащих указанному пользователю.

    :param user: Токен пользователя (JWT)
    :return: Список объектов проектов
    """
    try:
        payload = await token_utils.decode_jwt(user)
    except HTTPException as e:
        raise e

    # Извлекаем ID пользователя из токена
    user_id: str = payload.get("user_id")

    # TODO: Определить метод в crud_manager
    async with db_helper.session_factory() as session:
        stmt = (
            select(Project)
            .join(User, Project.prj_owner == User.id)
            .where(User.id == int(user_id), Project.deleted_at.is_(None))
        )
        results = await session.execute(stmt)
        projects: list[Project] = results.scalars().all()

        response_list = []
        for p in projects:
            response_list.append(ProjectResponseSchema.model_validate(p))
        return response_list


@router.get(
    "/{project_id}",
    include_in_schema=settings.run.dev_mode,
    response_model=ProjectResponseSchema,
)
async def get_project_by_id(
    project_id: str,
    access_token: str | bool = Depends(token_utils.check_access_token),
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    try:
        project_id = UUID(project_id)
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Неверный формат ID проекта. Используйте UUID"},
        )
    try:
        project = await crud_manager.project.get_project_by_id(project_uuid=project_id)
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Проект не найден"},
        )

    if project:
        return ProjectResponseSchema.model_validate(project[0])
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Проект не найден"},
        )


@router.delete(
    "/{project_id}",
    summary="Delete project by UUID and user owner ID",
    response_model=ProjectSchemas.BaseMessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "model": ProjectSchemas.BaseMessageResponse,
            "description": "Неверный формат ID проекта",
        },
        404: {
            "model": ProjectSchemas.BaseMessageResponse,
            "description": "Сообщение не найдено",
        },
        500: {
            "model": ProjectSchemas.BaseMessageResponse,
            "description": "Внутренняя ошибка сервера",
        },
    },
)
async def delete_project(
    project_id: str, user: str | bool = Depends(token_utils.check_access_token)
) -> ProjectSchemas.BaseMessageResponse | JSONResponse:
    """
    Удаляет проект с указанным ID. Удаление подразумевает добавление метки "deleted_at" в таблицу

    :param project_id: UUID проекта.
    :param user: JWT пользователя.
    :return: Словарь с сообщением о результате удаления проекта.
    """

    payload = await token_utils.decode_jwt(user)
    user_id: str = payload.get("user_id")

    try:
        project_id = UUID(project_id)
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Неверный формат ID проекта. Используйте UUID"},
        )

    # TODO: Определить метод в crud_manager
    async with db_helper.session_factory() as session:
        stmt = (
            select(Project)
            .join(User, Project.prj_owner == User.id)
            .where(
                User.id == user_id,
                Project.uuid == project_id,
                Project.deleted_at.is_(None),
            )
        )
        project = await session.scalar(stmt)
        if not project:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Запрашиваемый проект не найден"},
            )

        try:
            await crud_manager.project.delete(project.id)
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": f"Ошибка при удалении: {e}"},
            )

            # 5) Успешный ответ — FastAPI подхватит response_model
        return {"message": "Проект успешно удалён"}
