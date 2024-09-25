# import libraries
import asyncio

# import from libraries
from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# import from modules
from app.config.config import get_tokens

# create engine and connetion to DB
post_host_token = asyncio.run(get_tokens('POSTGRESQL_HOST'))
engine = create_async_engine(url=post_host_token, echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'atomlabreguser'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at = mapped_column(DateTime)
    date_bid: Mapped[str] = mapped_column(String(15), nullable=True)
    id_bid = mapped_column(BigInteger, nullable=True, unique=True)
    Fullname: Mapped[str] = mapped_column(String(250), nullable=True)


async def async_main() -> None:
    """
    func create all tables in database
    :return: None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


