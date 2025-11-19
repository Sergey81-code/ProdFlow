import os
from typing import Any, AsyncGenerator, Callable
from uuid import UUID

import pytest
import sqlalchemy
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.core.config import get_settings
from db.session import get_session
from main import app
from tests.testDAL import TestDAL

settings = get_settings()

DSN_FOR_TESTDAL = "".join(settings.TEST_DATABASE_URL.split("+asyncpg"))

CLEAN_TABLES = ["users", "roles", "devices"]

VERSION_URL = "/v1"
USER_URL = "/users"
DEVICE_URL = "/devices"
ROLE_URL = "/roles"
LOGIN_URL = "/auth"


# @pytest.fixture(scope="session")
# def event_loop():
#     return asyncio.get_event_loop()


# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="session")
async def async_session_test():
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest.fixture(scope="session", autouse=True)
async def run_migrations():
    alembic_ini_path = os.path.join(os.getcwd(), "tests", "alembic.ini")
    alembic_cfg = Config(alembic_ini_path)

    command.upgrade(alembic_cfg, "heads")
    yield


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test: AsyncSession):
    query = """
    TRUNCATE TABLE {tables}
    RESTART IDENTITY
    CASCADE;
    """.format(
        tables=",".join(CLEAN_TABLES)
    )

    async with async_session_test.begin() as session:
        await session.execute(sqlalchemy.text(query))


async def _get_test_session():
    test_engine = create_async_engine(
        settings.TEST_DATABASE_URL, future=True, echo=True
    )
    test_async_session = sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with test_async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[TestClient, Any]:
    """
    Create a new FastApi TestClient that uses the 'db_session' fixture to override
    the 'get_session' dependency that is injected into routers.
    """

    app.dependency_overrides[get_session] = _get_test_session
    with TestClient(app=app) as client:
        yield client


@pytest.fixture
async def get_project_settings():
    async def _get_project_settings():
        settings = get_settings()
        return settings

    return _get_project_settings


@pytest.fixture
async def get_role_from_database() -> Callable[[UUID], dict[str, Any] | None]:
    async def get_role_from_database_by_id(obj_id: UUID) -> dict[str, Any] | None:
        async with TestDAL(DSN_FOR_TESTDAL) as dal:
            role = await dal.get_obj_from_database_by_id("roles", obj_id)
            return dict(role) if role else None

    return get_role_from_database_by_id


@pytest.fixture
async def get_user_from_database() -> Callable[[UUID], dict[str, Any] | None]:
    async def get_user_from_database_by_id(obj_id: UUID) -> dict[str, Any] | None:
        async with TestDAL(DSN_FOR_TESTDAL) as dal:
            user = await dal.get_obj_from_database_by_id("users", obj_id)
            if user:
                user = dict(user)
                roles = await dal.get_all(
                    "roles",
                )
                user["roles"] = [
                    role for role in roles if role["id"] in user["role_ids"]
                ]
            return user

    return get_user_from_database_by_id


@pytest.fixture
async def get_device_from_database() -> Callable[[UUID], dict[str, Any] | None]:
    async def get_device_from_database_by_id(
        obj_id: UUID,
    ) -> dict[str, Any] | None:
        async with TestDAL(DSN_FOR_TESTDAL) as dal:
            device = await dal.get_obj_from_database_by_id("devices", obj_id)
            return dict(device) if device else None

    return get_device_from_database_by_id


@pytest.fixture
async def create_role_in_database() -> Callable[[dict[str | list[dict[str]]]], str]:
    async def create_role_in_database(role_info) -> str:
        async with TestDAL(DSN_FOR_TESTDAL) as dal:
            return await dal.create_object_in_database("roles", role_info)

    return create_role_in_database


@pytest.fixture
async def create_user_in_database() -> Callable[[dict[str | list[dict[str]]]], str]:
    async def create_user_in_database(user_info: dict) -> str:
        async with TestDAL(DSN_FOR_TESTDAL) as dal:
            user_id = await dal.create_object_in_database("users", user_info)
            full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')} {user_info.get('patronymic', '')}"
            await dal.add_tsvector_to_obj("users", user_id, "full_name_tsv", full_name)
            return user_id

    return create_user_in_database


@pytest.fixture
async def create_device_in_database() -> Callable[[dict[str | list[dict[str]]]], str]:
    async def create_device_in_database(device_info) -> str:
        async with TestDAL(DSN_FOR_TESTDAL) as dal:
            return await dal.create_object_in_database("devices", device_info)

    return create_device_in_database


@pytest.fixture
def user_data():
    return {
        "username": "test_username",
        "password": "StrongPass123!",
    }
