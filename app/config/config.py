import logging
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic_settings import PydanticBaseSettingsSource
from pydantic_settings import SettingsConfigDict
from pydantic_settings import YamlConfigSettingsSource

from config.database import DatabaseConfig
from config.log import LoggerConfig
from config.rabbitmq import RabbitMQConfig
from config.s3 import S3Config
from config.uvicorn import UvicornConfig

BASE_DIR = Path(__file__).resolve().parent.parent

log = logging.getLogger(__name__)


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
    uvicorn: UvicornConfig
    secrets: SecretsConfig
    s3: S3Config
    tg: TelegramAuthConfig


settings = Settings()
