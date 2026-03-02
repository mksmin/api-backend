import logging
from enum import StrEnum
from typing import Annotated
from typing import Any

from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import status
from fastapi.responses import JSONResponse

from app_exceptions import InvalidSignatureError
from app_exceptions import UnknownBotAuthError
from auth.auth_service import AuthService
from auth.verifiers_dispatcher import GetVerifierDispatcher
from auth.verifiers_dispatcher import VerifierDispatcher
from config import settings
from config.auth_bots import BotsEnum
from core.crud import GetCRUDService
from core.crud.crud_service import CRUDService

log = logging.getLogger(__name__)


class ClientType(StrEnum):
    TELEGRAM_WIDGET = "TelegramWidget"
    TELEGRAM_MINIAPP = "TelegramMiniApp"


async def _auth_tg_dep(
    bot_name: BotsEnum,
    body_data: str | dict[str, Any],
    auth_schema: ClientType,
    crud_service: CRUDService,
    verifier_dispatcher: VerifierDispatcher,
) -> JSONResponse:
    log.info(
        "Auth user via tg %s. Bot %s",
        auth_schema,
        bot_name,
    )
    auth_service = AuthService(
        verifier_dispatcher,
        crud_service,
    )
    try:
        auth_data = await auth_service.auth_user_via_bots(
            bot_name=bot_name,
            bot_data_str=body_data,
            client_type=auth_schema,
        )
    except UnknownBotAuthError as e:
        log.warning(
            "Unknown bot for authentication: %s",
            bot_name,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown bot for authentication",
        ) from e
    except InvalidSignatureError as e:
        log.warning(
            "Signature verification failed for bot %s: %s",
            bot_name,
            e,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        ) from e
    response = JSONResponse(
        content={
            "redirect_url": auth_data.get("redirect_path"),
        },
        status_code=status.HTTP_200_OK,
    )
    response.set_cookie(
        key="access_token",
        value=auth_data.get("access_token", ""),
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=settings.access_token.lifetime_seconds,
    )
    return response


async def auth_user_via_tg_miniapp_with_cookie(
    bot_name: Annotated[
        BotsEnum,
        Path(),
    ],
    body_data: Annotated[
        str,
        Body(),
    ],
    crud_service: GetCRUDService,
    verifier_dispatcher: GetVerifierDispatcher,
) -> JSONResponse:
    return await _auth_tg_dep(
        bot_name,
        body_data,
        auth_schema=ClientType.TELEGRAM_MINIAPP,
        crud_service=crud_service,
        verifier_dispatcher=verifier_dispatcher,
    )


async def auth_user_via_tg_widget_with_cookie(
    bot_name: Annotated[
        BotsEnum,
        Path(),
    ],
    body_data: Annotated[
        dict[str, Any],
        Body(),
    ],
    crud_service: GetCRUDService,
    verifier_dispatcher: GetVerifierDispatcher,
) -> JSONResponse:
    return await _auth_tg_dep(
        bot_name,
        body_data,
        auth_schema=ClientType.TELEGRAM_WIDGET,
        crud_service=crud_service,
        verifier_dispatcher=verifier_dispatcher,
    )


AuthUserViaTgMiniapp = Annotated[
    JSONResponse,
    Depends(auth_user_via_tg_miniapp_with_cookie),
]
AuthUserViaTgWidget = Annotated[
    JSONResponse,
    Depends(auth_user_via_tg_widget_with_cookie),
]
