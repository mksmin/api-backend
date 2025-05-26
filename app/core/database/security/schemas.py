from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class APIKeyBase(BaseModel):
    """
    Base model for API keys.

    This class represents the base model for API keys. It contains fields for the revoked status and the expiration time of the key.
    """

    revoked: bool = Field(False, description="Отозван ли ключ")
    expires_at: Optional[datetime] = Field(
        None,
        description="Время истечения ключа",
        example=datetime.now(),
    )


class APIKeyCreate(APIKeyBase):
    """
    Model for creating API keys.

    This class represents the model for creating API keys. It inherits from the APIKeyBase class.
    """


class APIKeyUpdate(APIKeyBase):
    """
    Model for updating API keys.

    This class represents the model for updating API keys. It inherits from the APIKeyBase class and contains a field for updating the revoked status of the key.
    """

    revoked: Optional[bool] = Field(None, description="Обновление статуса ключа")


class APIKeyOut(APIKeyBase):
    """
    Model for outputting API keys.

    This class represents the model for outputting API keys. It inherits from the APIKeyBase class and contains fields for the key identifier, key prefix, and creation time.
    """

    id: int = Field(..., description="Идентификатор ключа")
    key_prefix: str = Field(..., description="Префикс ключа", example="123456")
    created_at: datetime = Field(
        ..., description="Дата создания ключа", example=datetime.now()
    )

    class Config:
        from_attributes = True


class APIKeyFull(APIKeyOut):
    """
    Model for full API keys.

    This class represents the model for full API keys. It inherits from the APIKeyOut class and contains a field for the key itself.
    """

    key: str = Field(
        ...,
        description="Ключ",
        example="1234567890abcdef1234567890abcdef",
        max_length=47,
    )
