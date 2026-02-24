from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
)

from config import settings
from utils import camel_case_converter


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(naming_convention=settings.db.naming_convention)

    @declared_attr.directive
    def __tablename__(self) -> str:
        return f"{camel_case_converter(self.__name__)}s"
