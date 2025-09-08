from typing import Any

from fastapi import Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from api.api_v2.auth import token_utils
from api.api_v2.dependencies import (
    FRONTEND_DIR,
)


TEMPLATES = Jinja2Templates(directory=FRONTEND_DIR / "templates")


def return_template_for_affirmations(
    request: Request,
    user_id: str = Depends(token_utils.soft_validate_access_token),
) -> dict[str, Any]:
    return {
        "request": request,
        "content_template": None if user_id else "auth_widget.html",
        "user": True if user_id else None,
    }
