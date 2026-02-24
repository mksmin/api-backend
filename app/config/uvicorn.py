from pydantic import BaseModel


class UvicornConfig(BaseModel):
    host: str
    port: int
    dev_mode: bool
    workers: int = 1
    unix_socket: bool = False
