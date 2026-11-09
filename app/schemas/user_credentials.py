from typing import Self

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator
from pydantic_core import PydanticCustomError


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
        if not isinstance(value, str):
            error_type = "invalid_email"
            msg = "Invalid email address"
            raise PydanticCustomError(
                error_type,
                msg,
            )
        return value.strip().lower()


class LoginCredentialsForm(CredentialsForm): ...


class CreateCredentialsForm(CredentialsForm):
    password_confirm: str

    @model_validator(
        mode="after",
    )
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            error_type = "passwords_do_not_match"
            msg = "Passwords doesn't match"
            raise PydanticCustomError(
                error_type,
                msg,
            )
        return self


class ChangeUserCredentialsForm(BaseModel):
    email: EmailStr = Field(
        max_length=254,
    )
    old_password: str = Field(
        min_length=8,
        max_length=1024,
    )
    password: str = Field(
        min_length=8,
        max_length=1024,
    )
    password_confirm: str = Field(
        max_length=1024,
    )

    @model_validator(
        mode="after",
    )
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            error_type = "passwords_do_not_match"
            msg = "Passwords doesn't match"
            raise PydanticCustomError(
                error_type,
                msg,
            )
        return self


class CredentialsReadSchema(BaseModel):
    email: EmailStr | None
    email_confirmed: bool
