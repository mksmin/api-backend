import json
import re

from app.core import logger
from app.core.database import User

FIELD_MAPPING: dict[str, str] = {
    "second_name": "last_name",
    "first_name": "first_name",
    "patronymic": "middle_name",
    "birthday": "birth_date",
    "email": "email",
    "mobile": "mobile",
    "competention": "track",
    "country": "country",
    "city": "city",
    "citizenship": "citizenship",
    "school": "study_place",
    "class_number": "grade_level",
    "sex": "sex",
    "timezone": "timezone",
    "project_id": "project_id",
    "date_bid": "date_bid_ya",
    "id_bid": "id_bid_ya",

}
MODEL_FIELDS = User.get_model_fields()


def json_key_to_model_field(json_key: str) -> str:
    # Удаляем суффикс типа (_str, _date и т.д.)
    key_without_suffix = json_key.rsplit('_', 1)[0]

    # Конвертируем CamelCase в snake_case
    snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', key_without_suffix).lower()
    # Возвращаем соответствующее значение из маппинга
    return FIELD_MAPPING.get(snake_case, snake_case)


def map_json_to_model(json_data: dict) -> dict:
    return {
        json_key_to_model_field(k): v
        for k, v in json_data.items()
        if json_key_to_model_field(k) in MODEL_FIELDS
    }


async def get_data_from_json(parameters: dict) -> dict[str, str]:
    answers = parameters.get('answers')
    answers_dict = json.loads(answers)
    data_answers = answers_dict['answer']['data']

    result = {}
    for key, value in data_answers.items():
        if isinstance(value['value'], list):
            value = value['value'][0]['text']
        else:
            value = value['value']

        result[key] = value

    result['DateBid'] = answers_dict.get('created')  # Дата заявки в форме Яндекса
    result['IdBid'] = answers_dict.get('id')  # ID заявки на из формы Яндекса

    # Переименование ключей в соответствии с маппингом User
    mapping_keys: dict[str, str] = map_json_to_model(result)

    return mapping_keys
