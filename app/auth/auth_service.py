import logging

from app_exceptions.exceptions import UnsupportedClientTypeError
from auth.verifiers.base import AuthPayload
from auth.verifiers_dispatcher import VerifierDispatcher
from config.auth_bots import ClientType
from core.crud.crud_service import CRUDService
from schemas import UserCreateSchema
from schemas import UserSchema

log = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        verifier_dp: VerifierDispatcher,
        crud_service: CRUDService,
    ) -> None:
        self.verifier_dp = verifier_dp
        self.crud = crud_service

    async def auth_user_via_bots(
        self,
        bot_data: AuthPayload,
        auth_schema: ClientType,
    ) -> UserSchema:
        if auth_schema not in list(ClientType):
            log.warning(
                "Unsupported client type: %s",
                auth_schema,
            )
            error_msg = f"Unsupported client type: {auth_schema}"
            raise UnsupportedClientTypeError(error_msg)

        strategy = self.verifier_dp.get(
            auth_schema=auth_schema,
        )
        user_data = UserCreateSchema.model_validate(
            await strategy.verify(bot_data),
        )

        return await self.crud.user.create_or_get_user(user_data)
