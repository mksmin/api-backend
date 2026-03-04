import logging
from typing import Annotated
from typing import Any

from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import status
from fastapi.responses import JSONResponse

from app_exceptions import InvalidPayloadError
from app_exceptions import InvalidSignatureError
from auth import jwt_helper
from auth.auth_service import AuthService
from auth.verifiers.base import AuthPayload
from auth.verifiers.base import TelegramMiniappPayload
from auth.verifiers.base import TelegramOIDCPayload
from auth.verifiers.base import TelegramWidgetPayload
from auth.verifiers_dispatcher import GetVerifierDispatcher
from auth.verifiers_dispatcher import VerifierDispatcher
from config import settings
from config.auth_bots import BotsEnum
from config.auth_bots import ClientType
from core.crud import GetCRUDService
from core.crud.crud_service import CRUDService

log = logging.getLogger(__name__)


async def _auth_tg_dep(
    redirect_path: str,
    body_data: AuthPayload,
    auth_schema: ClientType,
    crud_service: CRUDService,
    verifier_dispatcher: VerifierDispatcher,
) -> JSONResponse:
    log.info(
        "Auth user via tg %s",
        auth_schema,
    )
    auth_service = AuthService(
        verifier_dispatcher,
        crud_service,
    )
    try:
        user = await auth_service.auth_user_via_bots(
            auth_schema=auth_schema,
            bot_data=body_data,
        )

    except InvalidPayloadError as e:
        log.warning(
            "Invalid data for auth via schema %s",
            auth_schema,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data",
        ) from e
    except InvalidSignatureError as e:
        log.warning(
            "Signature verification failed for schema %s",
            auth_schema,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        ) from e

    jwt_token = await jwt_helper.sign_jwt_token(user.id)
    log.info(
        "Tokens generated | User: %d | JWT expiry: %d",
        user.id,
        settings.access_token.lifetime_seconds,
    )
    response = JSONResponse(
        content={
            "redirect_url": redirect_path,
        },
        status_code=status.HTTP_200_OK,
    )
    response.set_cookie(
        key="access_token",
        value=str(jwt_token.get("access_token", "")),
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
    data = TelegramMiniappPayload(
        bot_name=bot_name,
        data=body_data,
    )
    return await _auth_tg_dep(
        redirect_path=settings.bots[bot_name].redirect_path,
        body_data=data,
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
    data = TelegramWidgetPayload(
        bot_name=bot_name,
        data=body_data,
    )
    return await _auth_tg_dep(
        redirect_path=settings.bots[bot_name].redirect_path,
        body_data=data,
        auth_schema=ClientType.TELEGRAM_WIDGET,
        crud_service=crud_service,
        verifier_dispatcher=verifier_dispatcher,
    )


async def auth_user_via_tg_oidc_with_cookie(
    bot_name: Annotated[
        BotsEnum,
        Path(),
    ],
    oidc_token: Annotated[
        str,
        Body(),
    ],
    crud_service: GetCRUDService,
    verifier_dispatcher: GetVerifierDispatcher,
) -> JSONResponse:
    data = TelegramOIDCPayload(
        bot_name=bot_name,
        client_id=settings.bots[bot_name].client_id,
        id_token=oidc_token,
    )
    return await _auth_tg_dep(
        redirect_path=settings.bots[bot_name].redirect_path,
        body_data=data,
        auth_schema=ClientType.TELEGRAM_OPENID,
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
AuthUserViaTgOIDC = Annotated[
    JSONResponse,
    Depends(auth_user_via_tg_oidc_with_cookie),
]
