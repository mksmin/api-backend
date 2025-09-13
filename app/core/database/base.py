from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from core import settings
from utils import camel_case_converter


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(naming_convention=settings.db.naming_convention)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_converter(cls.__name__)}s"
