# import libraries
import asyncio
import json
import jwt
import hmac
import hashlib
import secrets


# import from libraries
from datetime import datetime, timedelta
from fastapi import Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from jwt import ExpiredSignatureError, InvalidTokenError
from pathlib import Path
from urllib.parse import parse_qsl, unquote, parse_qs


from app.core import settings, logger


BASE_DIR = Path.cwd().parent  # project working directory api_atomlab/app
FRONTEND_DIR = (
    (BASE_DIR / "api-atom-front") if settings.run.dev_mode else (BASE_DIR / "frontend")
)
HTML_DIR = FRONTEND_DIR / "src"
STATIC_DIR = FRONTEND_DIR / "public"
templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")
not_found_404 = FRONTEND_DIR / "src/404.html"


JWT_SECRET = settings.api.secret
JWT_ALGORITHM = settings.api.algorithm
ACCESS_TOKEN_EXPIRE_HOURS = 1


BOT_CONFIG = {
    "bot1": {
        "name": "atombot",
        "redirect_uri": "/profile",
    },
    "bot2": {
        "name": "mininbot",
        "redirect_uri": "/affirm",
    },
    "bot3": {
        "name": "testbot",
        "redirect_uri": "/profile",
    },
}


def token_response(token: str) -> dict:
    return {"access_token": token, "token_type": "bearer"}


async def sign_csrf_token():
    return secrets.token_urlsafe(32)


async def sign_jwt_token(user_id: int) -> dict:
    """
    Создаёт JWT-токен для авторизации
    :param user_id: int
    :return: dict[str, str] = {"access_token": str, "token_type": "bearer"}
    """

    payload = {
        "sub": str(user_id),
        "exp": (
            datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        ).timestamp(),
        "iat": datetime.now().timestamp(),  # issued at (время создания)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


async def decode_jwt(token: str) -> dict:
    """
    Decodes a JWT token and returns a dictionary with the decoded token information.

    :param token: (str) The JWT token to be decoded.
    :return: (dict) A dictionary with the decoded token information.
    :raises: (HTTPException) If the token is expired or invalid.
    """

    try:
        decoded_token = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": True}
        )
        return {
            "success": True,
            "user_id": decoded_token["sub"],
            "issued_at": decoded_token["iat"],
            "expires_at": decoded_token["exp"],
        }
    except ExpiredSignatureError:
        print(f"Token ExpiredSignatureError")
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError:
        print(f"Token InvalidTokenError")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_telegram_data(raw_query: str, bot_token: str) -> bool:
    """
    Проверяет валидность данных от Telegram MiniApps
    """
    try:

        # Разбираю строку запроса, получая список кортежей (ключ, значение)
        pairs = parse_qsl(raw_query, keep_blank_values=True)
        data_dict = dict(pairs)

        print(f"data_dict: {data_dict}")

        input_hash = data_dict.get("hash", None)
        if not input_hash:
            return False

        # Сортирую по ключам
        sorted_pairs = sorted(
            [(k, v) for k, v in pairs if k != "hash"],
            key=lambda x: x[0],
        )

        # Формирую список со строками для хеширования
        data_check_list = [f"{k}={v}" for k, v in sorted_pairs]

        # Собираю общую строку
        data_check_str = "\n".join(data_check_list)

        # Генерация секретного ключа
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256,
        ).digest()

        # Генерация хэша
        generated_hash = hmac.new(
            secret_key,
            data_check_str.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Защита от атаки по времени
        return hmac.compare_digest(generated_hash, input_hash)

    except Exception as e:
        raise ValueError(f"Verification error: {e}")


def verify_telegram_widget(raw_query: str, bot_token: str) -> bool:
    """
    Проверяет валидность данных от Telegram Widget
    :param raw_query:
    :param bot_token:
    :return:
    """
    try:
        pairs = parse_qs(raw_query, keep_blank_values=True)
        data = {k: v[0] for k, v in pairs.items()}

        # Извлекаем hash и удаляем его из словаря
        received_hash = data.pop("hash", None)

        if not received_hash:
            print("Параметр hash не найден в данных.")
            return False

        # Формируем строку проверки: сортируем ключи и объединяем их в формате "ключ=значение",
        # разделяя строки символом перевода строки "\n"
        data_check_arr = []
        for key in sorted(data.keys()):
            data_check_arr.append(f"{key}={data[key]}")
        data_check_string = "\n".join(data_check_arr)

        # Вычисляем секретный ключ: SHA256-хэш от токена бота
        secret_key = hashlib.sha256(bot_token.encode()).digest()

        # Вычисляем HMAC-SHA256 от data_check_string, используя secret_key
        hmac_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        # print(f"hmac_hash: {hmac_hash}")
        # print(f"received_hash: {received_hash}")

        # Сравниваем вычисленный хэш с полученным (безопасное сравнение)
        return hmac.compare_digest(hmac_hash, received_hash)
    except Exception as e:
        raise ValueError(f"Widget verification error: {e}")


# Общая зависимость верификации данных от Telegram
async def verify_telegram_data_dep(
    request: Request, bot_name: str, client_type: str
) -> bool:
    try:
        # Получаю данные тела запроса для валидации от телеграма
        raw_data = await request.body()
        raw_data_str = raw_data.decode()

        if not raw_data_str:
            logger.error('"raw_data_str" is empty')
            raise HTTPException(status_code=400, detail="Missing data")

        try:
            logger.info(f"client_type: {client_type}")
            if client_type == "TelegramWidget":
                verify_result = verify_telegram_widget(
                    raw_data_str, settings.api.bot_token[bot_name]
                )
            elif client_type == "TelegramMiniApp":
                verify_result = verify_telegram_data(
                    raw_data_str, settings.api.bot_token[bot_name]
                )
            else:
                logger.error(
                    '"client_type" is not "TelegramMiniApp" or "TelegramWidget"'
                )
                raise HTTPException(status_code=400, detail="Invalid client type")

        except ValueError as e:
            logger.error('"raw_data_str" is not valid')
            raise HTTPException(status_code=401, detail=str(e))

        if not verify_result:
            logger.error('"raw_data_str" is not valid')
            raise HTTPException(status_code=401, detail="Invalid data")

        return True
        # return parse_qsl(raw_data_str, keep_blank_values=True)

    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def verify_client(request: Request) -> str:
    # Определяю тип клиента из заголовка
    client_source = request.headers.get("X-Client-Source", None)
    allowed_clients = ["TelegramMiniApp", "TelegramWidget"]

    if client_source not in allowed_clients:
        raise HTTPException(400, "Invalid client")

    return client_source


def get_verified_data(bot_name: str):
    async def dependency(request: Request, client_type: str = Depends(verify_client)):
        verified_data = await verify_telegram_data_dep(request, bot_name, client_type)
        return verified_data

    return dependency


async def verified_data_dependency(
    request: Request,
    bot_name: str,
    client_type: str = Depends(verify_client),
):
    print(f"bot_name: {bot_name}")

    bot_data = BOT_CONFIG.get(bot_name, None)
    if not bot_data:
        raise HTTPException(status_code=404, detail="Bot not Found")

    dependency_func = get_verified_data(bot_data["name"])
    return await dependency_func(request, client_type)


# Общая функция для обработки профиля
async def process_profile(template_name: str, data_dict_for_template):

    return templates.TemplateResponse(template_name, data_dict_for_template)


async def extract_user_data(data_dict: dict) -> dict:
    user_data = json.loads(data_dict["user"])
    return {
        "id": user_data.get("id"),
        "first_name": user_data.get("first_name", None),
        "last_name": user_data.get("last_name", None),
        "username": user_data.get("username", None),
        "is_premium": user_data.get("is_premium", None),
        "photo_url": user_data.get("photo_url", None),
        "language_code": user_data.get("language_code", None),
        "allows_write_to_pm": user_data.get("allows_write_to_pm", None),
    }
