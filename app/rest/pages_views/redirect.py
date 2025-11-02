import logging

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.requests import Request

from auth import jwt_helper

log = logging.getLogger(__name__)


async def redirect_to_login_page(
    request: Request,
    user_id: str = Depends(
        jwt_helper.soft_validate_access_token,
    ),
) -> None:
    if not user_id:
        login_url = request.url_for("auth:login").include_query_params(
            redirect_url=str(request.url.path),
        )
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": str(login_url)},
        )
