# import lib
import json
import pprint

# import from lib
from fastapi import APIRouter, Depends, Header, Body
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path

# import from modules
from app.core import logger
from app.core import crud as rq

from .auth import auth_handler as ah
from .json_helper import get_data_from_json

router = APIRouter()


@router.get('/statistics/', include_in_schema=False)
async def get_statistics(token=Header()) -> JSONResponse:
    """
    Функция подключается к БД и возвращает ответы в JSON
    :param token:
    :return: JSONResponse
    """

    decode_result = await ah.decode_jwt(token)
    if not decode_result['message']['success']:
        message = {"message": {'error': decode_result['message']['error']}}
        mess_to_json = json.dumps(message)
        return JSONResponse(content=mess_to_json, status_code=400)

    try:
        # result = await rq.get_registration_stat('atomlabreguser')
        logger.info('Функция запроса статистики пользователя успешно прошла')
    except Exception as e:
        logger.warning(f'Ошибка при работе с БД: {e}')
        message_error = {"message": {"error": "Возникла проблема с базой данных"}}
        message_to_json = json.dumps(message_error)
        return JSONResponse(content=message_to_json, status_code=500)

    #
    # total_users = list(result[0][0])[0]
    # result_dict = {"total_users": total_users, "details": {}}
    #
    # for dict_items in result[1]:
    #     competention, count = dict_items.keys()
    #     result_dict['details'][dict_items[competention]] = dict_items[count]
    # message = {"message": result}
    # mess_to_json = json.dumps(message)
    mess_to_json = 'Успешно'
    return JSONResponse(content=mess_to_json, status_code=200)


@router.post('/registration', include_in_schema=False)
async def registration(data=Body()):
    params = data.get('params')
    dict_user = await get_data_from_json(
        parameters=params
    )

    result = await rq.create.create_user_from_dict(dict_values=dict_user)

    if result[0]:
        return JSONResponse(content={"message": result[1]}, status_code=201)

    return JSONResponse(content={"message": result[1]}, status_code=500)


@router.post('/get_token/{user_id}', include_in_schema=False)
async def get_token(user_id: int):
    if not isinstance(user_id, int):
        return JSONResponse(content={"message": f"{user_id} is not an integer"}, status_code=400)

    result = await ah.sign_jwt(user_id)
    return JSONResponse(content=result, status_code=201)
