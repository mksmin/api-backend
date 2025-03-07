# import libraries
import os
import json

# import from libraries
from fastapi import APIRouter, Body, Header
from fastapi.responses import JSONResponse, FileResponse

# import from modules
from app.config.config import logger
import app.database.requests as rq
import app.api.auth.auth_handler as ah

cwd = os.getcwd()
dirname = os.path.dirname(__file__)
path_dirname = os.path.dirname(dirname)
cwd_project_path = os.path.normpath(os.path.dirname(path_dirname))
not_found_404 = os.path.join(cwd_project_path, 'html/404.html')

getapp = APIRouter()


async def check_path(path_file: str):
    file_exists = os.path.exists(str(path_file))
    is_file = os.path.isfile(str(path_file))

    if file_exists and is_file:
        return path_file, 200
    else:
        return not_found_404, 404


@getapp.get("/")
async def index_page():
    index_html = os.path.join(cwd_project_path, "html/index.html")
    return FileResponse(index_html)


@getapp.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(cwd_project_path, "favicon.ico")
    return FileResponse(favicon_path)


@getapp.get("/robots.txt", include_in_schema=False)
async def robots():
    robots_path = os.path.join(cwd_project_path, "robots.txt")
    return FileResponse(robots_path)


@getapp.get('/html/{name_html}', include_in_schema=False)
async def html_path(name_html: str):
    media_path = os.path.join(cwd_project_path, "html/", name_html)
    result, status = await check_path(media_path)
    return FileResponse(result, status_code=status)


@getapp.get('/html/media/{name_media}', include_in_schema=False)
async def html_path(name_media: str):
    media_path = os.path.join(cwd_project_path, "html/media/", name_media)
    result, status = await check_path(media_path)
    return FileResponse(result, status_code=status)


@getapp.get('/html/style/{name_style}', include_in_schema=False)
async def html_path(name_style: str):
    media_path = os.path.join(cwd_project_path, "html/style", name_style)
    result, status = await check_path(media_path)
    return FileResponse(result, status_code=status)


@getapp.get('/statistics/', include_in_schema=False)
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
        result = await rq.get_registration_stat('atomlabreguser')
    except Exception as e:
        message_error = {"message": {"error": "Возникла проблема с базой данных"}}
        message_to_json = json.dumps(message_error)
        return JSONResponse(content=message_to_json, status_code=500)

    total_users = list(result[0][0])[0]
    result_dict = {"total_users": total_users, "details": {}}

    for dict_items in result[1]:
        competention, count = dict_items.keys()
        result_dict['details'][dict_items[competention]] = dict_items[count]
    message = {"message": result_dict}
    mess_to_json = json.dumps(message)

    return JSONResponse(content=mess_to_json, status_code=200)
