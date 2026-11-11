from pydantic import BaseModel
from pydantic import SecretStr
from sqlalchemy import URL


class DatabaseConfig(BaseModel):
    name: str
    host: str
    port: int
    user: str
    password: SecretStr

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

    @property
    def async_url(self) -> URL:
        is_socket = self.host.startswith("/")

        return URL.create(
            drivername="postgresql+asyncpg",
            database=self.name,
            host=None if is_socket else self.host,
            port=None if is_socket else self.port,
            username=self.user,
            password=self.password.get_secret_value(),
            query={
                "host": self.host,
            }
            if is_socket
            else {},
        )
