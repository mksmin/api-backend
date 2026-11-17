from pydantic import Field
from pydantic_settings import BaseSettings


class LMSSettings(BaseSettings):
    enabled: bool = False
    organizer_user_ids: set[int] = Field(
        default_factory=set,
    )

    def can_create_project(
        self,
        user_id: int,
    ) -> bool:
        return user_id in self.organizer_user_ids
