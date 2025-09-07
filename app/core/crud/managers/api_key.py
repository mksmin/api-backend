from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
import datetime

from core.crud.managers import BaseCRUDManager
from core.database.security.models import APIKey
from core.database.security import utils as ut


class APIKeyManager(BaseCRUDManager[APIKey]):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory, model=APIKey)

    async def create(
        self, *, project_id: int, temporary: bool = True
    ) -> tuple[str, APIKey]:
        raw_key, hashed_key = await ut.generate_api_key_and_hash()

        new_api_key = {
            "key_hash": hashed_key,
            "project_id": project_id,
            "key_prefix": raw_key[:11],
        }
        if temporary:
            new_api_key.update(
                {
                    "expires_at": datetime.datetime.now() + datetime.timedelta(days=45),
                }
            )

        instance = await super().create(**new_api_key)

        return (
            raw_key,
            instance,
        )
