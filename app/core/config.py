import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import unquote, quote

from pydantic import BaseModel, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y/%m/%d %H:%M:%S")
        return formatter.format(record)


log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "app.log"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
    )
)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"
    dev_mode: bool = False


class ApiV2Prefix(BaseModel):
    prefix: str = "/v2"
    users: str = "/users"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v2: ApiV2Prefix = ApiV2Prefix()

    bot_token: dict = {"bot_name": "1234567890:DefaultBotToken"}
    secret: str = "default_secret"
    algorithm: str = "HS256"


class RabbitMQConfig(BaseModel):
    host: str = "localhost"
    port: int = 5672
    username: str = "user"
    password: str = "wpwd"
    vhostname: str = "vhost"

    @computed_field
    @property
    def url(self) -> str:
        safe_username = quote(self.username, safe="")
        safe_password = quote(self.password, safe="")
        safe_vhost = quote(self.vhostname, safe="")

        return f"amqp://{safe_username}:{safe_password}@{self.host}:{self.port}/{safe_vhost}"


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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="API_CONFIG__",
    )
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    run: RunConfig = RunConfig()
    rabbit: RabbitMQConfig = RabbitMQConfig()


settings = Settings()
