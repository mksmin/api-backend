from fastapi import Query
from pydantic import BaseModel


# Схема для параметров запроса
class ProjectFilter(BaseModel):
    owner_tg_id: int
    limit: int | None
    offset: int | None

    @classmethod
    def from_query(
        cls,
        owner_tg_id: int = Query(
            ...,
            description="tg_id пользователя",
        ),
        limit: int | None = Query(None, description="Лимит"),
        offset: int | None = Query(None, description="Смещение"),
    ) -> "ProjectFilter":

        return cls(
            owner_tg_id=owner_tg_id,
            limit=limit,
            offset=offset,
        )
