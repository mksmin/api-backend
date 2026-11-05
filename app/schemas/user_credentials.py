from typing import Self

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator


class CredentialsForm(BaseModel):
    email: EmailStr = Field(
        max_length=254,
    )
    password: str = Field(
        min_length=8,
        max_length=1024,
    )

    @field_validator(
        "email",
        mode="before",
    )
    @classmethod
    def normalize_email(
        cls,
        value: str,
    ) -> str:
        return value.strip().lower()


class LoginCredentialsForm(CredentialsForm): ...


class CreateCredentialsForm(CredentialsForm):
    password_confirm: str

    @model_validator(
        mode="after",
    )
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            msg = "Passwords doesn't match"
            raise ValueError(msg)
        return self


class CredentialsReadSchema(BaseModel):
    email: EmailStr | None
    email_confirmed: bool
