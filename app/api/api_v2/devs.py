from fastapi import APIRouter, Cookie, HTTPException
from fastapi.responses import JSONResponse

from app.core import settings
from .auth import access_token_helper as token_utils


router = APIRouter(
    prefix="/devs",
)


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/token/decode", include_in_schema=settings.run.dev_mode)
async def decode_token(token: str | None = Cookie(default=None, alias="access_token")):
    try:
        payload = await token_utils.decode_jwt(token)
        return payload
    except HTTPException as he:
        return JSONResponse(content={"error": he.detail}, status_code=400)


@router.post("/token/{user_id}", include_in_schema=settings.run.dev_mode)
async def create_token(user_id: int):
    if not isinstance(user_id, int):
        return JSONResponse(
            content={"message": f"{user_id} is not an integer"}, status_code=400
        )
    jwt_token = await token_utils.sign_jwt_token(int(user_id))

    response = JSONResponse(content=jwt_token, status_code=201)
    # Устанавливаю куки
    response.set_cookie(
        key="access_token",
        value=jwt_token["access_token"],
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=settings.access_token.lifetime_seconds,
    )
    return response
