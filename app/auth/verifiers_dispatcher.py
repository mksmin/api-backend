import logging
from typing import Annotated

from fastapi import Depends
from pydantic import SecretStr

from app_exceptions.exceptions import UnsupportedClientTypeError
from auth.verifiers.base import BaseVerifier
from auth.verifiers.tg_miniapp import TelegramMiniAppVerifier
from auth.verifiers.tg_widget import TelegramWidgetVerifier
from config.auth_bots import ClientType

log = logging.getLogger(__name__)


class VerifierDispatcher:
    def __init__(self) -> None:
        self._registry: dict[
            ClientType,
            type[BaseVerifier],
        ] = {}

    def register(
        self,
        client_type: ClientType,
        verifier_class: type[BaseVerifier],
    ) -> None:
        if client_type in self._registry:
            error_msg = f"Verifier for {client_type} already registered"
            raise ValueError(error_msg)
        if not isinstance(verifier_class, type):
            error_msg = "Registered verifier must be a class"
            raise TypeError(error_msg)
        if not issubclass(verifier_class, BaseVerifier):
            error_msg = f"{verifier_class.__name__} must inherit from BaseVerifier"
            raise TypeError(error_msg)
        self._registry[client_type] = verifier_class
        log.info("Registered verifier for %s", client_type)

    def get(
        self,
        client_type: ClientType,
        bot_token: str | SecretStr,
    ) -> BaseVerifier:
        try:
            verifier_class = self._registry[client_type]
        except KeyError as exc:
            error_msg = f"Verifier for {client_type} not registered"
            raise UnsupportedClientTypeError(error_msg) from exc

        if isinstance(bot_token, SecretStr):
            bot_token = bot_token.get_secret_value()

        return verifier_class(bot_token=bot_token)


verifier_dispatcher = VerifierDispatcher()
verifier_dispatcher.register(ClientType.TELEGRAM_WIDGET, TelegramWidgetVerifier)
verifier_dispatcher.register(ClientType.TELEGRAM_MINIAPP, TelegramMiniAppVerifier)


def get_dispatcher() -> VerifierDispatcher:
    return verifier_dispatcher


GetVerifierDispatcher = Annotated[
    VerifierDispatcher,
    Depends(get_dispatcher),
]
