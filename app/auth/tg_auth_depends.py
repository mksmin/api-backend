import json
import logging
from enum import StrEnum
from typing import Annotated
from typing import Any

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.requests import Request

from auth.jwt_helper import BOT_CONFIG
from auth.tg_data_verify import verification_mini_apps_data
from auth.tg_data_verify import verification_widget_data
from config import settings

log = logging.getLogger(__name__)


class ClientType(StrEnum):
    TELEGRAM_WIDGET = "TelegramWidget"
    TELEGRAM_MINIAPP = "TelegramMiniApp"

    def get_verifier(
        self,
        tg_data_str: str,
        bot_token: str,
    ) -> bool:
        verifiers = {
            self.TELEGRAM_WIDGET: verification_widget_data,
            self.TELEGRAM_MINIAPP: verification_mini_apps_data,
        }

        if self not in verifiers:
            log.error(
                '"%s" is not "TelegramMiniApp" or "TelegramWidget"',
                self,
            )
            message_error = "Invalid client type"
            raise ValueError(message_error)
        return verifiers[self](
            tg_data_str,
            bot_token,
        )


ALLOWED_CLIENTS = list(ClientType)


async def verify_telegram_data_dep(
    request: Request,
    bot_name: str,
    client_type: str,
) -> bool:
    try:
        raw_data_str = (await request.body()).decode()
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

        client_type_enum = ClientType(client_type)
        try:
            verify_result = client_type_enum.get_verifier(
                raw_data_str,
                settings.secrets.bots_tokens[bot_name],
            )
            if not verify_result:
                log.error(
                    '"raw_data_str" is not valid, client_type: %s, bot_name: %s',
                    client_type,
                    bot_name,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid data",
                )
        except ValueError as e:
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
        return verify_result


async def verify_client(
    request: Request,
) -> str:
    client_source = request.headers.get("X-Client-Source", None)

    if not client_source:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing client source",
        )
    try:
        return ClientType(client_source)
    except ValueError as e:
        log.exception("Invalid client source: %s", client_source)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client",
        ) from e


async def verified_tg_data_dependency(
    request: Request,
    bot_name: str,
    client_type: Annotated[str, Depends(verify_client)],
) -> bool:
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
            detail="Bot not found",
        )

    return await verify_telegram_data_dep(
        request,
        bot_data["name"],
        client_type,
    )


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
