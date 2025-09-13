import hashlib
import hmac
import json
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, parse_qsl, unquote

from fastapi import Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse

from core import logger, settings
from core.crud import crud_manager

from .access_token_helper import BOT_CONFIG

BASE_DIR = Path.cwd().parent  # project working directory api_atomlab/app
FRONTEND_DIR = (
    (BASE_DIR / "api-atom-front")
    if settings.run.dev_mode
    else (BASE_DIR.parent / "frontend")
)
HTML_DIR = FRONTEND_DIR / "src"
STATIC_DIR = FRONTEND_DIR / "public"
templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")
not_found_404 = FRONTEND_DIR / "src/404.html"


def verify_telegram_data(raw_query: str, bot_token: str) -> bool:
    """
    Проверяет валидность данных от Telegram MiniApps
    """
    try:

        # Разбираю строку запроса, получая список кортежей (ключ, значение)
        pairs = parse_qsl(raw_query, keep_blank_values=True)
        data_dict = dict(pairs)

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
            b"WebAppData",
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
        result = hmac.compare_digest(generated_hash, input_hash)
        logger.debug(f"verify_telegram_data | result: {result}")
        return result

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
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        # print(f"hmac_hash: {hmac_hash}")
        # print(f"received_hash: {received_hash}")

        # Сравниваем вычисленный хэш с полученным (безопасное сравнение)
        return hmac.compare_digest(hmac_hash, received_hash)
    except Exception as e:
        raise ValueError(f"Widget verification error: {e}")


# Общая зависимость верификации данных от Telegram
async def verify_telegram_data_dep(
    request: Request,
    bot_name: str,
    client_type: str,
) -> bool:
    try:
        # Получаю данные тела запроса для валидации от телеграма
        raw_data = await request.body()
        raw_data_str = raw_data.decode()

        logger.debug(
            f"verify_telegram_data_dep | "
            f"client_type: {client_type} | "
            f"bot_name: {bot_name}",
        )

        if not raw_data_str:
            logger.error('"raw_data_str" is empty', exc_info=True)
            raise HTTPException(status_code=400, detail="Missing data")

        try:
            logger.info(f"Client_type: {client_type}")
            if client_type == "TelegramWidget":
                verify_result = verify_telegram_widget(
                    raw_data_str,
                    settings.api.bot_token[bot_name],
                )
            elif client_type == "TelegramMiniApp":
                verify_result = verify_telegram_data(
                    raw_data_str,
                    settings.api.bot_token[bot_name],
                )
            else:
                logger.error(
                    '"client_type" is not "TelegramMiniApp" or "TelegramWidget"',
                    exc_info=True,
                )
                raise HTTPException(status_code=400, detail="Invalid client type")

        except ValueError as e:
            logger.error('"raw_data_str" is not valid', exc_info=True)
            raise HTTPException(status_code=401, detail=str(e))

        if not verify_result:
            logger.error('"raw_data_str" is not valid', exc_info=True)
            raise HTTPException(status_code=401, detail="Invalid data")

        return True

    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Verification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def verify_client(request: Request) -> str:
    # Определяю тип клиента из заголовка
    client_source = request.headers.get("X-Client-Source", None)
    allowed_clients = ["TelegramMiniApp", "TelegramWidget"]

    if client_source not in allowed_clients:
        logger.error(
            f"Invalid client source: {client_source}",
            exc_info=True,
        )
        raise HTTPException(400, "Invalid client")

    return client_source


def get_verified_data(
    bot_name: str,
) -> Callable[[Request, str], Coroutine[Any, Any, bool]]:
    async def dependency(
        request: Request,
        client_type: str = Depends(verify_client),
    ) -> bool:
        return await verify_telegram_data_dep(request, bot_name, client_type)

    return dependency


async def verified_data_dependency(
    request: Request,
    bot_name: str,
    client_type: str = Depends(verify_client),
) -> dict[str, str | bool]:
    logger.debug(
        f"Verified data dependency | "
        f"request: {request.url.path} | "
        f"bot_name: {bot_name} | "
        f"client_type: {client_type}",
    )

    bot_data = BOT_CONFIG.get(bot_name, None)
    if not bot_data:
        raise HTTPException(status_code=404, detail="Bot not Found")

    dependency_func: bool = await verify_telegram_data_dep(
        request,
        bot_data["name"],
        client_type,
    )
    result: dict[str, str | bool] = {
        "is_authorized": dependency_func,
        "client_type": client_type,
    }

    # TODO: После успешной проверки зарегистрировать пользователя (решить где это делать)
    if dependency_func:
        raw_data = await request.body()
        raw_data_str = raw_data.decode()
        if client_type == "TelegramWidget":
            windget_pairs = parse_qs(raw_data_str, keep_blank_values=True)
            data = {
                k: v[0]
                for k, v in windget_pairs.items()
                if k not in ("hash", "auth_date")
            }
        else:
            logger.info("Зашел в блок TelegramMiniApp, чтобы спарсить данные")
            miniapp_pairs: list[tuple[str, str]] = parse_qsl(
                raw_data_str,
                keep_blank_values=True,
            )
            data_dict = dict(miniapp_pairs)
            data = await extract_user_data(data_dict)

        logger.debug(f"Verified data dependency | " f"data: {data}")
        data["tg_id"] = data.pop("id")
        user = await crud_manager.user.create(data)
        logger.debug(f"Получен пользователь: {user}")

    return result


# Общая функция для обработки профиля
async def process_profile(
    template_name: str,
    data_dict_for_template: dict[str, Any],
) -> HTMLResponse:
    return templates.TemplateResponse(template_name, data_dict_for_template)


async def extract_user_data(
    data_dict: dict[str, Any],
) -> dict[str, Any]:
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
