# import lib
import pandas as pd

# import from lib
from fastapi import APIRouter, Cookie, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from io import StringIO
from typing import Annotated

# import from modules
from core import settings, crud_manager, logger
from .auth import access_token_helper as token_utils

router = APIRouter(
    prefix="/devs",
    tags=["Devs API"],
)


async def validate_csv(file: UploadFile):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are allowed"
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


@router.post("/csv_to_db", include_in_schema=settings.run.dev_mode)
async def temp_upload_csv(file: Annotated[UploadFile, File()]):
    # Валидация файла
    await validate_csv(file)

    try:
        # Чтение и парсинг CSV
        contents = await file.read()
        csv_string = StringIO(contents.decode("utf-8"))
        df = pd.read_csv(csv_string)

        # Проверка наличия данных
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file is empty"
            )

        # Конвертация DataFrame в список словарей
        data = df.to_dict(orient="records")

        for user in data:
            user.pop("id")
            user.pop("created_at")
            user.pop("copmetention")

            await crud_manager.user.create(data=user)

    except Exception as e:
        logger.error(f"Ошибка при загрузке CSV: {e}")
