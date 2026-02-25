from urllib.parse import quote

from pydantic import BaseModel
from pydantic import computed_field


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
