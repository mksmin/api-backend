__all__ = (
    "GetCRUDService",
    "connector",
    "crud_manager",
    "get_registration_stat",
)

from core.crud.crud_service import GetCRUDService

from .config import connector
from .crud_manager import crud_manager
from .read import get_registration_stat
