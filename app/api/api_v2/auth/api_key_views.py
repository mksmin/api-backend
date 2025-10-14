from datetime import datetime, timezone

from fastapi import APIRouter

from core.database.security import schemas as sch
from core.database.security import utils as ut

router = APIRouter(
    prefix="/api-key",
)


@router.post(
    "/generate",
    response_model=sch.APIKeyFull,
)
async def generate_api_key(
    data: sch.APIKeyCreate,
) -> sch.APIKeyFull:
    raw_key, _ = await ut.generate_api_key_and_hash()
    db_response = {
        "id": 1,
        "created_at": datetime.now(timezone.utc),
    }

    return sch.APIKeyFull(
        **db_response,
        key=raw_key,
        key_prefix=raw_key[:11],
        project_id=data.project_id,
    )
