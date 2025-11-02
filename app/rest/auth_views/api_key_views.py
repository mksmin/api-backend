from datetime import datetime, timezone

from fastapi import APIRouter

from core.database.security import (
    schemas,
    utils,
)

router = APIRouter(
    prefix="/api-key",
)


@router.post(
    "/generate",
    response_model=schemas.APIKeyFull,
)
async def generate_api_key(
    data: schemas.APIKeyCreate,
) -> schemas.APIKeyFull:
    raw_key, _ = await utils.generate_api_key_and_hash()
    db_response = {
        "id": 1,
        "created_at": datetime.now(timezone.utc),
    }

    return schemas.APIKeyFull(
        **db_response,
        key=raw_key,
        key_prefix=raw_key[:11],
        project_id=data.project_id,
    )
