from pydantic import BaseModel


class UserDataReadSchema(BaseModel):
    id: int
    tg_id: int
    first_name: str | None
    last_name: str | None
    username: str | None
    is_premium: bool | None = None
    photo_url: str | None = None
    language_code: str | None = None
    allows_write_to_pm: bool | None = None
