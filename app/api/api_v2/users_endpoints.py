# import lib
import json
import pandas as pd

# import from lib
from io import StringIO
from typing import Annotated
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
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel

# import from modules
from app.core import logger
from app.core.crud import crud_manager, get_registration_stat
from app.core.database.schemas import ProjectResponseSchema, ProjectRequestSchema
from .auth import auth_utils, token_utils, auth_handler

from .json_helper import get_data_from_json

router = APIRouter()


@router.get("/statistics/", include_in_schema=False)
async def get_statistics(token=Header()) -> JSONResponse:
    """
    Функция подключается к БД и возвращает ответы в JSON
    :param token:
    :return: JSONResponse
    """

    decode_result = await token_utils.decode_jwt(token)
    if not decode_result["message"]["success"]:
        message = {"message": {"error": decode_result["message"]["error"]}}
        mess_to_json = json.dumps(message)
        return JSONResponse(content=mess_to_json, status_code=400)

    try:
        result = await get_registration_stat("users")
        logger.debug("Функция запроса статистики пользователя успешно прошла")

    except Exception as e:
        logger.warning(f"Ошибка при работе с БД: {e}")
        message_error = {"message": {"error": "Возникла проблема с базой данных"}}
        message_to_json = json.dumps(message_error)
        return JSONResponse(content=message_to_json, status_code=500)

    message = {"message": result}
    mess_to_json = json.dumps(message)
    return JSONResponse(content=mess_to_json, status_code=200)


@router.post("/registration", include_in_schema=False)
async def registration(data=Body()):
    params = data.get("params")
    dict_user = await get_data_from_json(parameters=params)

    result = await crud_manager.user.create(data=dict_user)

    if result:
        return JSONResponse(content={"message": "Success"}, status_code=201)

    return JSONResponse(content={"message": "Error"}, status_code=500)


@router.post("/get_token/{user_id}", include_in_schema=False)
async def get_token(user_id: int):
    if not isinstance(user_id, int):
        return JSONResponse(
            content={"message": f"{user_id} is not an integer"}, status_code=400
        )

    result = await token_utils.sign_jwt_token(user_id)
    return JSONResponse(content=result, status_code=201)


async def validate_csv(file: UploadFile):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are allowed"
        )


@router.post(
    "/projects",
    status_code=status.HTTP_201_CREATED,
    tags=["Projects"],
    response_model=ProjectResponseSchema,
    include_in_schema=False,
)
async def create_project(
    data: ProjectRequestSchema,
):
    db_data = data.model_dump(by_alias=True)
    try:
        result = await crud_manager.project.create(db_data)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e.errors())
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ProjectResponseSchema.model_validate(result)


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(project_id: int):
    try:
        await crud_manager.project.delete(project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
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
    "/projects",
    include_in_schema=False,
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


@router.post("/csv_to_db", include_in_schema=False)
async def temp_upload_csv(file: Annotated[UploadFile, File()]):
    # Валидация файла
    await validate_csv(file)

    try:
        # Чтение и парсинг CSV
        contents = await file.read()
        csv_string = StringIO(contents.decode("utf-8"))
        df = pd.read_csv(csv_string)

        # Проверка наличия данных
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file is empty"
            )

        # Конвертация DataFrame в список словарей
        data = df.to_dict(orient="records")

        for user in data:
            user.pop("id")
            user.pop("created_at")
            user.pop("copmetention")

            await crud_manager.user.create(data=user)

    except Exception as e:
        logger.error(f"Ошибка при загрузке CSV: {e}")
