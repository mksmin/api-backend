import logging
import re
from typing import ClassVar
from typing import Any

from pydantic import BaseModel
from pydantic import Field, field_validator

log = logging.getLogger(__name__)


class CustomFormatter(logging.Formatter):
    RESET = "\033[0m"
    COLORS: ClassVar[dict[str, Any]] = {
        "time": "\033[97m",
        "level": {
            logging.DEBUG: "\033[37m",
            logging.INFO: "\033[32m",
            logging.WARNING: "\033[33m",
            logging.ERROR: "\033[31m",
            logging.CRITICAL: "\033[31;1m",
        },
        "method": "\033[33m",
        "path": "\033[0m",
        "status": {
            "2": "\033[92m",
            "3": "\033[96m",
            "4": "\033[91m",
            "5": "\033[91m",
        },
        "location": "\033[35m",
        "errors": "\033[31m",
    }
    HTTP_LOG_REGEX = re.compile(
        r'"(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD).*?" (\d{3})',
    )

    def format(self, record: logging.LogRecord) -> str:
        time_str = (
            f"{self.COLORS['time']}"
            f"[{self.formatTime(record, '%Y/%m/%d %H:%M:%S')}]"
            f"{self.RESET}"
        )
        level_str = (
            f"{self.COLORS['level'][record.levelno]}{record.levelname}:{self.RESET}"
        )

        msg = record.getMessage()

        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            msg = f"{self.COLORS['errors']}{msg}\n{exc_text}{self.RESET}"

        match = self.HTTP_LOG_REGEX.search(msg)
        if match:
            method = f"{self.COLORS['method']}{match.group(1)}{self.RESET}"
            status_code = match.group(2)
            status_color = self.COLORS["status"].get(status_code[0], self.RESET)
            status = f"{status_color}{status_code} {self.RESET}"

            start, end = match.span()

            main_msg = msg[
                start
                + len(match.group(1))
                + 1 : start
                + len(match.group(0))
                - len(match.group(2))
            ]

            msg = msg[:start] + status + method + main_msg + msg[end:]

        location_str = (
            f"{self.COLORS['location']}({record.filename}:{record.lineno}){self.RESET}"
        )

        return f"{time_str} {level_str} {msg} {location_str}"


console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())


class LoggerConfig(BaseModel):
    mode: str = Field(
        default="INFO",
        alias="mode",
        description="Уровень логирования: DEBUG, INFO",
    )

    @property
    def level(self) -> int:
        mapping = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
        }
        log.debug("mode: %s", self.mode)
        return mapping.get(self.mode.upper(), logging.INFO)

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        allowed_values = ["DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"]
        if value.upper() not in allowed_values:
            msg_error = (
                f"Уровень логирования должен быть одним из: {', '.join(allowed_values)}"
            )
            raise ValueError(msg_error)
        return value.upper()
