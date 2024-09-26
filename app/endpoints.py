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
path_json = os.path.join(os.path.dirname(dirname), "file3.json")




@app.get("/")
async def start():
    index_html = os.path.join(os.path.dirname(dirname), "/html/index.html")
    return {"Hello": "World", "text": "Это сервер для API. В целом тебе тут делать нечего"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(dirname), "favicon.ico")
    return FileResponse(favicon_path)


@app.post('/registration/')
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
        answers = json.loads(params['answers'])
        date_bid = params['Date']
        id_bid = params['ID']

    # print(f"{params = }, type = {type(params)}")
    # print(f"{answers = }, type = {type(answers)}")
    # print(f"{date_bid = }, type = {type(date_bid)}")
    # print(f"{id_bid = }, type = {type(id_bid)}")

    return {"Awnser": "Кажется, что все ок"}


def tmp_json_work():
    with open(path_json, encoding='utf-8') as f:
        data = json.load(f)
        params = data.get("params")
        answers = json.loads(params['answers'])
        date_bid = params['Date']
        id_bid = params['ID']
        keys_data = list(answers.keys())
        # print(data)
        # print(answers)
        pprint.pprint(answers)
        print(type(answers))

        pprint.pprint(params['Test'])

        return keys_data


@rq.connection
async def test(session, data_list):
    print(data_list)
    result = await rq.get_colums_name(session)
    print(f'{result = }')
    for i in data_list:
        if i not in result:
            await rq.add_column_for_db(session, i)


async def tmp_main():
    result = tmp_json_work()
    print(f'{result = }')
    # await test(result)


if __name__ == '__main__':
    # asyncio.run(tmp_main())
    print(None)
