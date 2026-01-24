import logging
import re
from pathlib import Path
from typing import Any, ClassVar
from urllib.parse import quote

from pydantic import (
    BaseModel,
    Field,
    PostgresDsn,
    computed_field,
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

BASE_DIR = Path(__file__).resolve().parent.parent


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
            f"{self.COLORS['level'][record.levelno]}"
            f"{record.levelname}:"
            f"{self.RESET}"
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
            f"{self.COLORS['location']}"
            f"({record.filename}:{record.lineno})"
            f"{self.RESET}"
        )

        return f"{time_str} {level_str} {msg} {location_str}"


log = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())


class AccessTokenSecretsConfig(BaseModel):
    secret: str


class AccessToken(BaseModel):
    lifetime_seconds: int
    algorithm: str
    secrets: AccessTokenSecretsConfig

    @property
    def secret(self) -> str:
        return self.secrets.secret


class ApiV2Prefix(BaseModel):
    prefix: str
    users: str


class ApiPrefix(BaseModel):
    prefix: str
    v2: ApiV2Prefix


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


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
                f"Уровень логирования должен быть одним из: "
                f"{', '.join(allowed_values)}"
            )
            raise ValueError(msg_error)
        return value.upper()


class RabbitSecretsConfig(BaseModel):
    username: str
    password: str


class RabbitMQConfig(BaseModel):
    host: str
    port: int
    vhostname: str
    secure: bool = True
    secrets: RabbitSecretsConfig

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        safe_username = quote(self.secrets.username, safe="")
        safe_password = quote(self.secrets.password, safe="")
        safe_vhost = quote(self.vhostname, safe="")
        protocol = "amqps" if self.secure else "amqp"

        return f"{protocol}://{safe_username}:{safe_password}@{self.host}:{self.port}/{safe_vhost}"


class RunConfig(BaseModel):
    host: str
    port: int
    dev_mode: bool
    workers: int = 1
    unix_socket: bool = False


class S3Config(BaseModel):
    access_key: str
    secret_key: str
    endpoint_url: str
    bucket_name: str


class SecretsConfig(BaseModel):
    bots_tokens: dict[str, str]
    session_secret: str


class TelegramAuthConfig(BaseModel):
    widget_bot_id: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="API_CONFIG__",
        yaml_file=(
            BASE_DIR / "config.default.yaml",
            BASE_DIR / "config.local.yaml",
        ),
        yaml_config_section="api-backend",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Define the sources and their order for loading the settings values.

        Args:
            settings_cls: The Settings class.
            init_settings: The `InitSettingsSource` instance.
            env_settings: The `EnvSettingsSource` instance.
            dotenv_settings: The `DotEnvSettingsSource` instance.
            file_secret_settings: The `SecretsSettingsSource` instance.

        Returns:
            A tuple containing the sources and their order
            for loading the settings values.
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSettingsSource(settings_cls),
        )

    access_token: AccessToken
    api: ApiPrefix
    db: DatabaseConfig
    log: LoggerConfig
    rabbit: RabbitMQConfig
    run: RunConfig
    secrets: SecretsConfig
    s3: S3Config
    tg: TelegramAuthConfig


settings = Settings()
