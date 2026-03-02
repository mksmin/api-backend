import logging
from enum import StrEnum

log = logging.getLogger(__name__)


class ClientType(StrEnum):
    TELEGRAM_WIDGET = "TelegramWidget"
    TELEGRAM_MINIAPP = "TelegramMiniApp"
