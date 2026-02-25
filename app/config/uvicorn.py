from pydantic import BaseModel


class UvicornConfig(BaseModel):
    host: str
    port: int
    workers: int = 1
    unix_socket: bool = False
