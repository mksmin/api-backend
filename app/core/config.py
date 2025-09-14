import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import ClassVar
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
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"
    format_str = "[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS: ClassVar[dict[int, str]] = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset,
    }

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y/%m/%d %H:%M:%S")
        return formatter.format(record)


log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "app.log"

logger = logging.getLogger(__name__)

# Консольноый логгер
console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())

# Файловый логгер
file_handler = RotatingFileHandler(
    filename=str(log_file),  # Явное преобразование в строку
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
    encoding="utf-8",
)
file_handler.setFormatter(
    logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
        "%Y/%m/%d %H:%M:%S",
    ),
)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


class AccessToken(BaseModel):
    lifetime_seconds: int
    secret: str
    algorithm: str


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
        logger.debug("mode: %s", self.mode)
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


class RabbitMQConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    vhostname: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        safe_username = quote(self.username, safe="")
        safe_password = quote(self.password, safe="")
        safe_vhost = quote(self.vhostname, safe="")

        return f"amqp://{safe_username}:{safe_password}@{self.host}:{self.port}/{safe_vhost}"


class RunConfig(BaseModel):
    host: str
    port: int
    dev_mode: bool


class SecretsConfig(BaseModel):
    bot_token: dict[str, str]


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


settings = Settings()
logger.setLevel(settings.log.level)
