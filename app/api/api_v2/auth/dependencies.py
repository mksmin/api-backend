import hashlib
import hmac
import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any
from urllib.parse import parse_qs, parse_qsl

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)

from core.config import settings
from core.crud import crud_manager

from .access_token_helper import BOT_CONFIG

log = logging.getLogger(__name__)


def verify_telegram_data(raw_query: str, bot_token: str) -> bool:
    """
    Проверяет валидность данных от Telegram MiniApps
    """
    try:

        # Разбираю строку запроса, получая список кортежей (ключ, значение)
        pairs = parse_qsl(raw_query, keep_blank_values=True)
        data_dict = dict(pairs)

        input_hash = data_dict.get("hash")
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
        log.debug("verify_telegram_data | result: %s", result)

    except (ValueError, KeyError, TypeError) as e:
        msg_error = f"Verification error: {e}"
        raise ValueError(msg_error) from e

    else:
        return result


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
            return False

        # Формируем строку проверки: сортируем ключи
        # и объединяем их в формате "ключ=значение",
        # разделяя строки символом перевода строки "\n"
        data_check_string = "\n".join(f"{key}={data[key]}" for key in sorted(data))

        # Вычисляем секретный ключ: SHA256-хэш от токена бота
        secret_key = hashlib.sha256(bot_token.encode()).digest()

        # Вычисляем HMAC-SHA256 от data_check_string, используя secret_key
        hmac_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Сравниваем вычисленный хэш с полученным (безопасное сравнение)
        return hmac.compare_digest(hmac_hash, received_hash)

    except (ValueError, KeyError, TypeError) as e:
        msg_error = f"Widget verification error: {e}"
        raise ValueError(msg_error) from e


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

        log.debug(
            "verify_telegram_data_dep | client_type: %s | bot_name: %s",
            client_type,
            bot_name,
        )

        if not raw_data_str:
            log.exception('"raw_data_str" is empty')
            raise HTTPException(  # noqa: TRY301
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing data",
            )

        try:
            log.info("Client_type: %s", client_type)
            if client_type == "TelegramWidget":
                verify_result = verify_telegram_widget(
                    raw_data_str,
                    settings.secrets.bots_tokens[bot_name],
                )
            elif client_type == "TelegramMiniApp":
                verify_result = verify_telegram_data(
                    raw_data_str,
                    settings.secrets.bots_tokens[bot_name],
                )
            else:
                log.exception(
                    '"client_type" is not "TelegramMiniApp" or "TelegramWidget"',
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid client type",
                )

            if not verify_result:
                log.error('"raw_data_str" is not valid')
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid data",
                )

        except ValueError as e:
            log.exception('"raw_data_str" is not valid')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid data",
            ) from e

    except HTTPException:
        raise

    except (UnicodeDecodeError, ValueError, KeyError) as e:
        log.exception("Verification error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

    else:
        return True


async def verify_client(request: Request) -> str:
    # Определяю тип клиента из заголовка
    client_source = request.headers.get("X-Client-Source", None)
    allowed_clients = ["TelegramMiniApp", "TelegramWidget"]

    if client_source not in allowed_clients:
        log.exception("Invalid client source: %s", client_source)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client",
        )

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
    log.debug(
        "Verified data dependency | "
        "request: %s | "
        "bot_name: %s | "
        "client_type: %s",
        request.url.path,
        bot_name,
        client_type,
    )

    bot_data = BOT_CONFIG.get(bot_name, None)
    if not bot_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not Found",
        )

    dependency_func: bool = await verify_telegram_data_dep(
        request,
        bot_data["name"],
        client_type,
    )
    result: dict[str, str | bool] = {
        "is_authorized": dependency_func,
        "client_type": client_type,
    }

    # TODO: После успешной проверки зарегистрировать пользователя
    # (решить где это делать)
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
            log.info("Зашел в блок TelegramMiniApp, чтобы спарсить данные")
            miniapp_pairs: list[tuple[str, str]] = parse_qsl(
                raw_data_str,
                keep_blank_values=True,
            )
            data_dict = dict(miniapp_pairs)
            data = await extract_user_data(data_dict)

        log.debug("Verified data dependency | data: %s", data)
        data["tg_id"] = data.pop("id")
        user = await crud_manager.user.create(data)
        log.debug("Получен пользователь: %s", user)

    return result


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
