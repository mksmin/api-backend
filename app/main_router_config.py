import logging
from typing import Literal

from fastapi import FastAPI
from fastapi import status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic_settings import BaseSettings
from starlette.middleware.sessions import SessionMiddleware

from api import router as api_router
from api.api_v2.health_views import router as health_router
from app_exceptions import RabbitMQServiceUnavailableError
from app_lifespan import lifespan
from auth.csrf_helper import CSRF_COOKIE_NAME
from auth.csrf_helper import CSRF_MAX_AGE
from config import settings
from paths_constants import FRONTEND_DIR_PATH
from paths_constants import templates
from rest.auth_views import router as auth_router
from rest.main_views import router as main_views_router
from rest.pages_views import router as pages_router
from rest.redirect import router as redirect_router
from subprojects.sdelkanv.main_views import router as sdelkanv_router

log = logging.getLogger(__name__)
AUTH_FORM_ROUTES = {
    "user:authenticate",
    "user:create-credentials",
    "user:change-password",
}
FORM_FIELD_LOCATION_LENGTH = 2
main_app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if settings.run.dev_mode else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.run.dev_mode else None,
)


main_app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR_PATH / "static",
        html=True,
    ),
)


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "https://api.xn----7sbbe2cen5a.xn--p1ai",
        "https://web.telegram.org",
    ],
    allow_methods=["POST"],
    allow_headers=["X-Client-Source", "Content-Type"],
    expose_headers=["X-Request-ID"],
)

main_app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secrets.session_secret,
    https_only=settings.run.auth_cookies_secure,
)


class CsrfSettings(BaseSettings):
    secret_key: str
    token_location: Literal["body"] = "body"  # noqa: S105
    token_key: str = "token_key"  # noqa: S105
    cookie_key: str = CSRF_COOKIE_NAME
    max_age: int = CSRF_MAX_AGE
    cookie_samesite: Literal["lax"] = "lax"
    cookie_secure: bool = True


@CsrfProtect.load_config
def get_csrf_settings() -> CsrfSettings:
    return CsrfSettings(
        secret_key=settings.secrets.csrf_secret.get_secret_value(),
        cookie_secure=settings.run.auth_cookies_secure,
    )


@main_app.exception_handler(
    RabbitMQServiceUnavailableError,
)
async def rabbitmq_service_unavailable_handler(
    request: Request,
    _exception: RabbitMQServiceUnavailableError,
) -> JSONResponse | HTMLResponse:
    log.warning(
        "Affirmation service timeout: %s",
        request.url.path,
    )

    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Affirmation service unavailable",
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="errors/service_unavailable.html",
        context={},
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@main_app.exception_handler(
    CsrfProtectError,
)
def csrf_protect_exception_handler(
    _request: Request,
    exc: CsrfProtectError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": str(exc.message),
        },
    )


@main_app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    route_name = getattr(request.scope.get("route"), "name", None)
    if route_name not in AUTH_FORM_ROUTES:
        return await request_validation_exception_handler(request, exc)

    detail = []
    for error in exc.errors():
        loc = error["loc"]
        kind = error["type"]
        field = (
            loc[1]
            if len(loc) == FORM_FIELD_LOCATION_LENGTH and loc[0] == "body"
            else None
        )

        if kind == "passwords_do_not_match":
            field = "password_confirm"
            code = "passwords_do_not_match"
        elif field == "email":
            code = "invalid_email"
        elif field in {"old_password", "password", "password_confirm"}:
            code = (
                "invalid_password_length"
                if kind in {"string_too_short", "string_too_long"}
                else "invalid_password"
            )
        else:
            continue

        detail.append({"loc": ["body", field], "type": code})

    return JSONResponse(
        status_code=422,
        content={"detail": detail or [{"loc": ["body"], "type": "invalid_form"}]},
    )


routers_for_include = (
    auth_router,
    api_router,
    redirect_router,
    main_views_router,
    pages_router,
    health_router,
    sdelkanv_router,
)

for router in routers_for_include:
    main_app.include_router(router)
