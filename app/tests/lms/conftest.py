import os
import shutil
import subprocess
import sys
from collections.abc import AsyncIterator
from collections.abc import Iterator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from auth.csrf_helper import csrf_token_for
from auth.jwt_helper import sign_jwt_token
from core.database import Project
from core.database import User
from core.database.db_helper import db_helper
from schemas import ProjectSchema
from schemas.lms.flows import LMSFlowsCreateSchema
from schemas.lms.flows import LMSFlowsReadSchema
from subprojects.lms.crud.services import LMSFlowsService

PROJECT_ROOT = Path(__file__).resolve().parents[3]
APP_DIR = PROJECT_ROOT / "app"
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.test.yaml"

TEST_DB_URL = "postgresql+asyncpg://test:test@127.0.0.1:55432/mini_lms_test"


@pytest.fixture(
    scope="session",
)
def test_db_url() -> Iterator[str]:
    docker = shutil.which("docker")
    if docker is None:
        pytest.fail(
            "Docker не найден. Установи и запусти Docker Desktop",
        )

    compose_command = [
        docker,
        "compose",
        "-f",
        str(COMPOSE_FILE),
    ]

    migration_env = os.environ.copy()
    migration_env.update(
        {
            "PYTHONPATH": str(APP_DIR),
            "API_CONFIG__DB__HOST": "127.0.0.1",
            "API_CONFIG__DB__PORT": "55432",
            "API_CONFIG__DB__NAME": "mini_lms_test",
            "API_CONFIG__DB__USER": "test",
            "API_CONFIG__DB__PASSWORD": "test",
        },
    )

    subprocess.run(  # noqa: S603
        [
            *compose_command,
            "up",
            "-d",
            "--wait",
            "--wait-timeout",
            "60",
        ],
        check=False,
    )

    try:
        subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "alembic",
                "upgrade",
                "head",
            ],
            cwd=APP_DIR,
            env=migration_env,
            check=True,
            timeout=120,
        )
        yield TEST_DB_URL

    finally:
        subprocess.run(  # noqa: S603
            [
                *compose_command,
                "down",
            ],
            cwd=PROJECT_ROOT,
            check=True,
            timeout=60,
        )


@pytest_asyncio.fixture
async def db_session(
    test_db_url: str,
) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(
        test_db_url,
        poolclass=NullPool,
    )

    try:
        async with engine.connect() as conn:
            transaction = await conn.begin()

            try:
                async with AsyncSession(
                    bind=conn,
                    join_transaction_mode="create_savepoint",
                    expire_on_commit=False,
                    autoflush=False,
                ) as session:
                    yield session
            finally:
                await transaction.rollback()
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def owner_id(
    db_session: AsyncSession,
) -> int:
    user = User(
        first_name="test_owner",
    )
    db_session.add(user)
    await db_session.commit()
    return user.id


@pytest_asyncio.fixture
async def outsider_id(
    db_session: AsyncSession,
) -> int:
    user = User(
        first_name="test_other_user",
    )
    db_session.add(user)
    await db_session.commit()
    return user.id


@pytest_asyncio.fixture
async def project(
    db_session: AsyncSession,
    owner_id: int,
) -> ProjectSchema:
    instance = Project(
        title="Test Project",
        description="Test Project Description",
        owner_id=owner_id,
    )
    db_session.add(instance)
    await db_session.commit()

    return ProjectSchema.model_validate(
        instance,
        context={
            "owner_uuid": None,
        },
    )


@pytest.fixture
def flows_service(
    db_session: AsyncSession,
) -> LMSFlowsService:
    return LMSFlowsService(db_session)


@pytest_asyncio.fixture
async def flow(
    flows_service: LMSFlowsService,
    project: ProjectSchema,
    owner_id: int,
) -> LMSFlowsReadSchema:
    return await flows_service.create_flow(
        project_id=project.id,
        flow_in=LMSFlowsCreateSchema(
            title="Test Flow",
        ),
        user_id=owner_id,
    )


@pytest_asyncio.fixture
async def owner_auth(
    owner_id: int,
) -> tuple[str, str]:
    token = await sign_jwt_token(
        owner_id,
    )
    return (
        str(
            token["access_token"],
        ),
        csrf_token_for(
            str(
                token["jti"],
            ),
        ),
    )


@pytest_asyncio.fixture
async def outsider_auth(
    outsider_id: int,
) -> tuple[str, str]:
    token = await sign_jwt_token(
        outsider_id,
    )
    return (
        str(
            token["access_token"],
        ),
        csrf_token_for(
            str(
                token["jti"],
            ),
        ),
    )


@pytest_asyncio.fixture
async def http_client(
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[AsyncClient]:
    from main_router_config import main_app  # noqa: PLC0415

    async def session_override() -> AsyncIterator[AsyncSession]:
        yield db_session

    monkeypatch.setitem(
        main_app.dependency_overrides,
        db_helper.session_getter,
        session_override,
    )

    async with AsyncClient(
        transport=ASGITransport(
            app=main_app,
        ),
        base_url="https://testserver",
        follow_redirects=False,
    ) as client:
        yield client
