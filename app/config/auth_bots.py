from enum import StrEnum

from pydantic import BaseModel
from pydantic import SecretStr


class BotsEnum(StrEnum):
    MININWORK_BOT = "mininwork_bot"
    TEST_MININBOT = "test_mininbot"


class ClientType(StrEnum):
    TELEGRAM_WIDGET = "TelegramWidget"
    TELEGRAM_MINIAPP = "TelegramMiniApp"


class AuthBots(BaseModel):
    redirect_path: str
    token: SecretStr
