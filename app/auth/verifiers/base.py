from abc import ABC
from abc import abstractmethod
from typing import Any

from config.auth_bots import BotsEnum


class AuthStrategy(ABC):
    @abstractmethod
    async def verify(self, *args: Any) -> Any:  # noqa: ANN401
        """Return true if signature is valid"""

    @classmethod
    @abstractmethod
    def factory(cls, bot_name: BotsEnum, **kwargs: str) -> "AuthStrategy": ...
