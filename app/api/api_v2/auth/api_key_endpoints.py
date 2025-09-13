# import from libs
from datetime import datetime

from fastapi import APIRouter

# import from modules
from core.database.security import schemas as sch
from core.database.security import utils as ut

# global
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
        "created_at": datetime.now(),
    }

    return sch.APIKeyFull(
        **db_response,
        key=raw_key,
        key_prefix=raw_key[:11],
    )


@router.get(
    "",
    response_model=sch.APIKeyOut,
)
async def get_api_key() -> sch.APIKeyOut:
    raw_key, _ = await ut.generate_api_key_and_hash()
    db_response = {
        "id": 1,
        "created_at": datetime.now(),
    }
    return sch.APIKeyOut(
        **db_response,
        key=raw_key,
        key_prefix=raw_key[:11],
    )
