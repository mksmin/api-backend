import json
import logging
from urllib.parse import parse_qsl

from app_exceptions import UnknownBotAuthError
from app_exceptions.exceptions import UnsupportedClientTypeError
from auth import jwt_helper
from auth.tg_auth_depends import ClientType
from auth.verifiers_dispatcher import VerifierDispatcher
from config import settings
from config.auth_bots import BotsEnum
from core.crud.crud_service import CRUDService
from schemas import UserCreateSchema

log = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        verifier_dp: VerifierDispatcher,
        crud_service: CRUDService,
    ) -> None:
        self.verifier_dp = verifier_dp
        self.crud = crud_service

    @classmethod
    def extract_data_from_bot_str(
        cls,
        bot_data_str: str,
        client_type: ClientType,
    ) -> UserCreateSchema:
        if client_type == client_type.TELEGRAM_MINIAPP:
            data_dict = dict(
                parse_qsl(
                    bot_data_str,
                    keep_blank_values=True,
                ),
            )
        elif client_type == client_type.TELEGRAM_WIDGET:
            data_dict = json.loads(bot_data_str)
        else:
            raise UnsupportedClientTypeError

        return UserCreateSchema.model_validate(data_dict)

    async def auth_user_via_bots(
        self,
        bot_name: BotsEnum,
        bot_data_str: str,
        client_type: ClientType,
    ) -> dict[str, str]:
        if bot_name not in settings.bots:
            log.warning(
                "Unknown bot requested: %s",
                bot_name,
            )
            error_msg = f"Unknown bot for authentication: {bot_name}"
            raise UnknownBotAuthError(error_msg)

        if client_type not in list(ClientType):
            log.warning(
                "Unsupported client type: %s",
                client_type,
            )
            error_msg = f"Unsupported client type: {client_type}"
            raise UnsupportedClientTypeError(error_msg)

        bot_setting = settings.bots[bot_name]

        verifier = self.verifier_dp.get(
            client_type=client_type,
            bot_token=bot_setting.token,
        )
        verifier.verify(bot_data_str)

        user_data = self.extract_data_from_bot_str(
            bot_data_str,
            client_type,
        )

        user = await self.crud.user.create_or_get_user(user_data)

        jwt_token = await jwt_helper.sign_jwt_token(user.id)
        log.info(
            "Tokens generated | User: %d | JWT expiry: %d",
            user.id,
            settings.access_token.lifetime_seconds,
        )
        return {
            "access_token": str(jwt_token.get("access_token", "")),
            "redirect_path": settings.bots[bot_name].redirect_path,
        }
