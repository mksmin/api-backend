# import libraries
import asyncio
import json
import os

# import from libraries
from fastapi import FastAPI, Body, UploadFile, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# import from modules
import app.database.requests as rq
from app.config.config import logger
from app.json_handlers import get_data_from_json

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

dirname = os.path.dirname(__file__)
path_dirname = os.path.normpath(os.path.dirname(dirname))
path_json = os.path.join(path_dirname, "tmp_files/file3.json")


@app.get("/")
async def index_page():
    index_html = os.path.join(path_dirname, "html/index.html")
    return FileResponse(index_html)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(dirname), "favicon.ico")
    return FileResponse(favicon_path)


@app.get("/robots.txt", include_in_schema=False)
async def robots():
    robots_path = os.path.join(os.path.dirname(dirname), "robots.txt")
    return FileResponse(robots_path)


@app.get('/html/{name_media}', include_in_schema=False)
async def html_path(name_media: str):
    media_path = os.path.join(path_dirname, "html/", name_media)
    not_found_404 = os.path.join(path_dirname, 'html/404.html')
    file_exists = os.path.exists(str(media_path))
    if not file_exists:
        return FileResponse(not_found_404)
    else:
        return FileResponse(media_path)


@app.post('/registration/', include_in_schema=False)
async def create_user(data=Body()):
    message_to_badreq = {"message": "Bad Request: You don't have "
                                    "the necessary parameters in the request body"}
    bad_request = JSONResponse(content=message_to_badreq, status_code=400)
    if data.get("params") is None:
        return bad_request
    else:
        params = data.get("params")  # dict
        prms_answers = params.get("answers")  # str
        prms_date_bid = params.get("Date")  # str
        prms_id_bid = params.get("ID")  # str

    if not prms_answers or not prms_date_bid or not prms_id_bid:
        # Проверяем, что требуемые параметры существуют в запросе
        return bad_request

    params_from_json = await get_data_from_json(params)  # получаем словарь из обработанного json

    colums_names_db = await rq.get_colums_name('atomlabreguser')  # Получаем список всех столбцов в БД
    difference_column = set([x.lower() for x in params_from_json]).difference(colums_names_db)

    if len(difference_column) > 0:
        # Если есть новые столбцы в запросе - создаем столбец в БД
        await rq.add_column_for_db(difference_column, 'atomlabreguser', params_from_json)

    try:
        # Сохраняем пользователя в БД
        await rq.set_user_registration(params_from_json, 'atomlabreguser')
    except Exception as e:
        text_message = {"message": str(e)}
        return JSONResponse(content=text_message, status_code=400)

    return {"Answer": "Кажется, что все ок"}


@app.post('/test/', include_in_schema=False)
async def tmp_test(data=Body()):
    pass


@rq.connection
async def test(session, data_list):
    print(data_list)
    result = await rq.get_colums_name(session)
    print(f'{result = }')
    for i in data_list:
        if i not in result:
            await rq.add_column_for_db(session, i)


async def tmp_main():
    pass
    # await test(result)


if __name__ == '__main__':
    asyncio.run(tmp_main())
    print(None)
