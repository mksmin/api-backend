import logging

from pydantic import BaseModel, PostgresDsn
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
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, '%Y/%m/%d %H:%M:%S')
        return formatter.format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Настраиваем логгер, используя созданный форматтер.
console_handler = logging.StreamHandler()
formatter = CustomFormatter()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"


class ApiV2Prefix(BaseModel):
    prefix: str = "/v2"
    users: str = "/users"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v2: ApiV2Prefix = ApiV2Prefix()

    secret: str = 'default_secret'
    algorithm: str = 'HS256'


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
        "pk": "pk_%(table_name)s"
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="API_CONFIG__"
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig


settings = Settings()
