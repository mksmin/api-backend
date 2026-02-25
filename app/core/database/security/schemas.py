from datetime import UTC
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class ProjectUUID(BaseModel):
    uuid: UUID


class APIKeyBase(BaseModel):
    """
    Base model for API keys.

    This class represents the base model for API keys.
    It contains fields for the revoked status and the expiration time of the key.
    """

    revoked: bool = Field(False, description="Отозван ли ключ")
    temporary: bool = Field(False, description="Временный ключ?")
    project_id: UUID = Field(..., description="Идентификатор проекта")
    expires_at: datetime | None = Field(None, description="Дата истечения ключа")


class APIKeyCreate(APIKeyBase):
    """
    Model for creating API keys.

    This class represents the model for creating API keys.
    It inherits from the APIKeyBase class.
    """


class APIKeyUpdate(APIKeyBase):
    """
    Model for updating API keys.

    This class represents the model for updating API keys.
    It inherits from the APIKeyBase class
    and contains a field for updating the revoked status of the key.
    """

    revoked: bool = Field(False, description="Обновление статуса ключа")


class APIKeyOut(APIKeyBase):
    """
    Model for outputting API keys.

    This class represents the model for outputting API keys.
    It inherits from the APIKeyBase class and contains fields for the key identifier,
    key prefix, and creation time.
    """

    id: int = Field(default=..., description="Идентификатор ключа")
    key_prefix: str = Field(
        default=...,
        description="Префикс ключа",
        examples=["123456"],
    )
    created_at: datetime = Field(
        default=...,
        description="Дата создания ключа",
        examples=[datetime.now(UTC)],
    )
    project_id: UUID = Field(..., description="Идентификатор проекта")

    class Config:
        from_attributes = True


class APIKeyFull(APIKeyOut):
    """
    Model for full API keys.

    This class represents the model for full API keys.
    It inherits from the APIKeyOut class and contains a field for the key itself.
    """

    key: str = Field(
        default=...,
        description="Ключ",
        examples=["1234567890abcdef1234567890abcdef"],
        max_length=47,
    )


class APIKeyCreateRequest(BaseModel):
    """
    Модель для вью, который создает API ключи.
    Используется для валидации входных данных.
    """

    temporary: bool = Field(False, description="Временный ключ")
    project_uuid: str = Field(..., description="Идентификатор проекта")


class APIKeyCreateResponse(BaseModel):
    """
    Модель для вью, который создает API ключи.
    Используется для разовой отправки не хэшированного ключа.
    """

    key: str = Field(
        ...,
        description="API Ключ",
        examples=["1234567890abcdef1234567890abcdef"],
        max_length=47,
    )
    key_prefix: str = Field(
        ...,
        description="Префикс ключа",
        examples=["tks_123lka"],
    )
    created_at: datetime = Field(
        ...,
        description="Дата создания ключа",
        examples=[datetime.now(UTC)],
    )
    expires_at: datetime | None = Field(None, description="Дата истечения ключа")
    project_uuid: UUID = Field(..., description="Идентификатор проекта")


class APIKeyGetResponse(BaseModel):
    """
    Модель для вью, который возвращает список API ключей проекта.
    Сырого ключа нет, только первые 11 символов.
    """

    key_prefix: str = Field(
        ...,
        description="Префикс ключа",
        examples=["tks_123lka"],
    )
    created_at: datetime = Field(
        ...,
        description="Дата создания ключа",
        examples=[datetime.now(UTC)],
    )
    expires_at: datetime | None = Field(None, description="Дата истечения ключа")
    project_id: UUID = Field(..., description="Идентификатор проекта")
    revoked: bool = Field(False, description="Отозван ли ключ")
