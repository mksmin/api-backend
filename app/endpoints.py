# import from libraries
import asyncio
import json
import os
import pprint

from typing import Annotated
from fastapi import FastAPI, Body, UploadFile, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import app.database.requests as rq
from app.config.config import logger

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
# app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# token: Annotated[str, Depends(oauth2_scheme)]

dirname = os.path.dirname(__file__)
path_dirname = os.path.normpath(os.path.dirname(dirname))
path_json = os.path.join(path_dirname, "tmp_files/file3.json")


@app.get("/")
async def start():
    index_html = os.path.join(path_dirname, "html/index.html")
    return FileResponse(index_html)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(dirname), "favicon.ico")
    return FileResponse(favicon_path)


@app.get('/html/{name_media}', include_in_schema=False)
async def html_path(name_media: str):
    media_path = os.path.join(path_dirname, "html/", name_media)
    file_exists = os.path.exists(str(media_path))
    if not file_exists:
        return JSONResponse(content={"message": "File is not found"}, status_code=404)
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
        params = data.get("params")
        answers = params.get("answers")
        date_bid = params.get("Date")
        id_bid = params.get("ID")

    if answers is None or date_bid is None or id_bid is None:
        return bad_request
    else:
        answers = params['answers']
        # date_bid = answers['created']
        # id_bid = answers['answer']['id']

    dict_ = {}
    for i in list(answers['answer']['data'].keys()):
        dict_[i] = answers['answer']['data'][i]['value']

    print(f'dict_ = {dict_}')

    # for i in list(dict_.keys()):
    #     split_list = i.split("_")
    #     name, type_name = split_list
    #     print(f"name: {name}, type_name: {type_name}")

    # print(f'date_bid = {date_bid}, id_bid = {id_bid}')

    return {"Awnser": "Кажется, что все ок"}


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
