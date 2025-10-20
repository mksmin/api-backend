__all__ = (
    "GetCRUDService",
    "connector",
    "get_registration_stat",
)

from core.crud.crud_service import GetCRUDService

from .config import connector
from .read import get_registration_stat
