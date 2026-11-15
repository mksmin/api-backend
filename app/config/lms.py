from pydantic_settings import BaseSettings


class LMSSettings(BaseSettings):
    enabled: bool = False
