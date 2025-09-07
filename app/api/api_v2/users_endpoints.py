# import lib
import json

# import from lib
from fastapi import (
    APIRouter,
    Header,
    Body,
    UploadFile,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# import from modules
from core import logger, settings
from core.crud import crud_manager, get_registration_stat
from core.database.schemas import ProjectResponseSchema, ProjectRequestSchema
from .auth import token_utils
from .user_projects import router as user_projects_router

from .json_helper import get_data_from_json

router = APIRouter()

router.include_router(user_projects_router)


@router.get("/statistics/", include_in_schema=settings.run.dev_mode)
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


@router.post("/registration", include_in_schema=settings.run.dev_mode)
async def registration(data=Body()):
    params = data.get("params")
    dict_user = await get_data_from_json(parameters=params)

    result = await crud_manager.user.create(data=dict_user)

    if result:
        return JSONResponse(content={"message": "Success"}, status_code=201)

    return JSONResponse(content={"message": "Error"}, status_code=500)


@router.post(
    "/projects",
    status_code=status.HTTP_201_CREATED,
    tags=["Projects"],
    response_model=ProjectResponseSchema,
    include_in_schema=settings.run.dev_mode,
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
