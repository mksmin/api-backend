from enum import StrEnum

from pydantic import BaseModel
from pydantic import SecretStr


class BotsEnum(StrEnum):
    WORKBOT = "mininwork_bot"
    TESTBOT = "test_mininbot"
    MAXBOT = "max_bot"


class AuthBots(BaseModel):
    redirect_path: str
    token: SecretStr
