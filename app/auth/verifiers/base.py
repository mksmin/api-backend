from abc import ABC
from abc import abstractmethod
from typing import Any

from app_exceptions import InvalidSignatureError


class BaseVerifier(ABC):

    def __init__(self, bot_token: str) -> None:
        self._bot_token = bot_token

    @abstractmethod
    def verify(self, raw_data: Any) -> Any:  # noqa: ANN401
        """Return true if signature is valid"""
        raise InvalidSignatureError
