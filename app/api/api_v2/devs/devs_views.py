from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Cookie,
    HTTPException,
    status,
)
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from api.api_v2.auth import access_token_helper as token_utils
from core import settings

from .dependencies import (
    create_token_by_user_id,
    read_and_parse_csv,
)

router = APIRouter()


@router.post(
    "/token/decode",
    include_in_schema=settings.run.dev_mode,
)
async def decode_token(
    token: Annotated[
        str | None,
        Cookie(
            default=None,
            alias="access_token",
        ),
    ],
) -> dict[str, Any]:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is missing",
        )

    try:
        return await token_utils.decode_jwt(token)
    except HTTPException as he:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=he.detail,
        )


@router.post(
    "/token/{user_id}",
    include_in_schema=settings.run.dev_mode,
)
async def create_token(
    user_id: int,
    jwt_token: Annotated[
        dict[str, Any],
        Depends(create_token_by_user_id),
    ],
) -> JSONResponse:

    response = JSONResponse(
        content=jwt_token,
        status_code=status.HTTP_201_CREATED,
    )
    response.set_cookie(
        key="access_token",
        value=jwt_token["access_token"],
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=settings.access_token.lifetime_seconds,
    )
    return response


@router.post(
    "/csv_to_db",
    include_in_schema=settings.run.dev_mode,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(read_and_parse_csv),
    ],
)
async def temp_upload_csv() -> str:
    return "Upload success"
