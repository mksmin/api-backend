from fastapi import APIRouter, Header, Body
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter()

actual_version = '/api/v2/'

path_mapping = {
    'users': actual_version+'users/',
}

@router.get('/statistics/', include_in_schema=False)
async def get_statistics(token=Header()) -> RedirectResponse:
    return RedirectResponse(url=f"{path_mapping['users']}statistics", status_code=308)


@router.post('/registration', include_in_schema=False)
async def registration(data=Body()):
    return RedirectResponse(url=f"{path_mapping['users']}registration", status_code=308)


@router.post('/get_token/{user_id}', include_in_schema=False)
async def get_token(user_id: int):
    return RedirectResponse(url=f"{path_mapping['users']}get_token/{user_id}", status_code=308)
