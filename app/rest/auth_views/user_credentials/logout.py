from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import status
from fastapi.responses import RedirectResponse
from fastapi_csrf_protect import CsrfProtect

from auth.csrf_helper import require_csrf_token
from config import settings

router = APIRouter()


@router.post(
    "/logout",
    status_code=status.HTTP_303_SEE_OTHER,
    name="user:logout",
    dependencies=[Depends(require_csrf_token)],
)
async def logout(
    request: Request,
    csrf_protect: Annotated[
        CsrfProtect,
        Depends(),
    ],
) -> RedirectResponse:
    response = RedirectResponse(
        url=request.url_for("auth:login"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=settings.run.auth_cookies_secure,
        httponly=True,
        samesite="lax",
    )
    request.session.pop("_csrf", None)
    csrf_protect.unset_csrf_cookie(response)
    return response
