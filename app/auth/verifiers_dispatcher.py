import logging
from collections.abc import Callable
from functools import partial
from typing import Annotated

from fastapi import Depends

from app_exceptions.exceptions import UnsupportedClientTypeError
from auth.verifiers.base import AuthStrategy
from auth.verifiers.tg_miniapp import TelegramMiniAppVerifier
from auth.verifiers.tg_oidc import TelegramOIDCVerifier
from auth.verifiers.tg_widget import TelegramWidgetVerifier
from config.auth_bots import BotsEnum
from config.auth_bots import ClientType

log = logging.getLogger(__name__)


class VerifierDispatcher:
    def __init__(self) -> None:
        self._registry: dict[
            ClientType,
            Callable[[BotsEnum], AuthStrategy],
        ] = {}

    def register(
        self,
        auth_schema: ClientType,
        factory: Callable[[BotsEnum], AuthStrategy],
    ) -> None:
        if auth_schema in self._registry:
            error_msg = f"Verifier for {auth_schema} already registered"
            raise ValueError(error_msg)

        self._registry[auth_schema] = factory
        log.info("Registered verifier for %s", auth_schema)

    def get(
        self,
        auth_schema: ClientType,
        bot_name: BotsEnum,
    ) -> AuthStrategy:
        try:
            factory = self._registry[auth_schema]
        except KeyError as exc:
            error_msg = f"Verifier for {auth_schema} not registered"
            raise UnsupportedClientTypeError(error_msg) from exc

        return factory(bot_name)


verifier_dispatcher = VerifierDispatcher()
verifier_dispatcher.register(
    ClientType.TELEGRAM_WIDGET,
    TelegramWidgetVerifier.factory,
)
verifier_dispatcher.register(
    ClientType.TELEGRAM_MINIAPP,
    TelegramMiniAppVerifier.factory,
)
verifier_dispatcher.register(
    ClientType.TELEGRAM_OPENID,
    partial(
        TelegramOIDCVerifier.factory,
        oid_server="https://oauth.telegram.org",
    ),
)


def get_dispatcher() -> VerifierDispatcher:
    return verifier_dispatcher


GetVerifierDispatcher = Annotated[
    VerifierDispatcher,
    Depends(get_dispatcher),
]
