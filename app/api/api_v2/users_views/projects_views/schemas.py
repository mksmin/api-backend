
from fastapi import Query
from pydantic import BaseModel


# Схема для параметров запроса
class ProjectFilter(BaseModel):
    owner_id: int
    limit: int | None
    offset: int | None

    @classmethod
    def from_query(
        cls,
        owner_id: int = Query(
            ...,
            description="tg_id пользователя",
            alias="project_owner",
        ),
        limit: int | None = Query(None, description="Лимит"),
        offset: int | None = Query(None, description="Смещение"),
    ) -> "ProjectFilter":

        return cls(
            owner_id=owner_id,
            limit=limit,
            offset=offset,
        )
