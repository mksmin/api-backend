from collections.abc import Iterator

import pytest
from fastapi import status
from fastapi.routing import APIRoute
from fastapi.routing import RouteContext
from fastapi.routing import iter_route_contexts
from fastapi.testclient import TestClient

from auth.redirects import safe_login_redirect
from config import settings
from main_router_config import main_app
from subprojects.lms import router as lms_router

LEGACY_PREFIXES = (
    "/projects",
    "/api/v2/users/projects",
)

TEST_UUID = "00000000-0000-4000-8000-000000000001"


@pytest.fixture
def client() -> Iterator[TestClient]:
    test_client = TestClient(main_app)
    yield test_client
    test_client.close()


def get_registered_routers() -> list[RouteContext]:
    return [
        context
        for context in iter_route_contexts(main_app.routes)
        if isinstance(
            context.original_route,
            APIRoute,
        )
    ]


def is_legacy_route(
    path: str,
) -> bool:
    return any(
        path == prefix or path.startswith(prefix + "/") for prefix in LEGACY_PREFIXES
    )


def test_legacy_project_routes_follow_feature_flag() -> None:
    registered = get_registered_routers()
    assert registered

    for prefix in LEGACY_PREFIXES:
        legacy_routes = [
            (route.path, route.methods)
            for route in registered
            if route.path is not None
            and (route.path == prefix or route.path.startswith(prefix + "/"))
        ]

        assert legacy_routes == []


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/projects"),
        ("GET", f"/projects/{TEST_UUID}"),
        ("GET", "/api/v2/users/projects/"),
        ("POST", "/api/v2/users/projects/"),
        ("GET", f"/api/v2/users/projects/{TEST_UUID}"),
        ("DELETE", f"/api/v2/users/projects/{TEST_UUID}"),
    ],
)
def test_legacy_urls_return_404(
    client: TestClient,
    method: str,
    path: str,
) -> None:
    response = client.request(
        method=method,
        url=path,
        follow_redirects=False,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_lms_routes_are_preserved() -> None:
    route_names = {
        context.name
        for context in iter_route_contexts(
            lms_router.routes,
        )
        if isinstance(
            context.original_route,
            APIRoute,
        )
    }

    expected = {
        "lms:index-page",
        "lms-project:create",
        "lms-projects:create:submit",
        "lms-project:detail",
        "lms-flows:list",
        "lms-flow:create",
        "lms-flow:create:submit",
        "lms-flow:details",
    }

    assert expected <= route_names


def test_lms_routes_mounted_when_enabled() -> None:
    if not settings.lms.enabled:
        pytest.skip(
            "LMS модуль отключен в тестовой конфигурации",
        )

    registered = {route.name for route in get_registered_routers()}

    assert "lms:index-page" in registered
    assert "lms-flows:list" in registered
    assert "lms-flow:create" in registered


def test_legacy_projects_login_redirect_removed() -> None:
    assert safe_login_redirect("/projects") == "/profile"


def test_lms_login_redirect_preserved() -> None:
    assert safe_login_redirect("/lms") == "/lms/"
