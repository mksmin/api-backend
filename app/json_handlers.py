import json
import pprint


async def get_data_from_json(parameters: dict) -> dict:
    """
    The function accepts parameters from a json request from a Yandex form
    """
    prms_answers = parameters.get("answers")  # str
    answers_dict = json.loads(prms_answers)  # from str to python dict
    data_answer = answers_dict['answer']['data']
    date_bid = parameters.get('Date')
    id_bid = parameters.get('ID')

    dict_ = {}
    for i in list(data_answer):
        value = data_answer[i]['value']

        if isinstance(value, list):
            dict_[i] = value[0].get('text')
        else:
            dict_[i] = value

    result_dict_to_db = {}
    for name, value in dict_.items():
        column_name, column_type = name.split('_')
        result_dict_to_db[column_name.lower()] = {
            'value': str(value),
            'type': column_type
        }
    result_dict_to_db['idbid']={
        'value': int(id_bid),
        'type': 'int'
    }
    result_dict_to_db['datebid'] = {
        'value': date_bid,
        'type': 'date'
    }
    # pprint.pprint(result_dict_to_db)

    return result_dict_to_db
