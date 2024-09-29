# import from libraries
from fastapi import Body
from fastapi.responses import JSONResponse

# import from modules
from app.config.config import app
import app.database.requests as rq
from app.config.config import logger
from app.json_handlers import get_data_from_json


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
