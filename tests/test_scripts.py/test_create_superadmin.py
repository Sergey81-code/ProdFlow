import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from scripts.create_superadmin import (
    is_free_username,
    check_creation_super_role,
    is_valid_password,
    create_superadmin,
)

from db.models import User, Role, UserRole


async def test_is_valid_password():
    assert is_valid_password("StrongPass1!")
    assert not is_valid_password("Ab1!")
    assert not is_valid_password("StrongPass!")
    assert not is_valid_password("strongpass1!")
    assert not is_valid_password("StrongPass1")


async def test_is_free_username_returns_true(get_project_settings):
    settings = await get_project_settings()
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    AsyncSessionMaker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    free_username = "free_username"

    async with AsyncSessionMaker() as isolated_session:
        assert await is_free_username(free_username, isolated_session)


async def test_is_free_username_returns_false(
    get_project_settings, create_user_in_database
):
    settings = await get_project_settings()
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    AsyncSessionMaker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    user_data = {
        "id": uuid4(),
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "employee_number": "some_token123",
        "password": "StrongPass123!",
    }

    await create_user_in_database(user_data)

    async with AsyncSessionMaker() as isolated_session:
        assert not await is_free_username(user_data["username"], isolated_session)


async def test_check_creation_super_role_returns_id(
    get_project_settings, create_role_in_database
):
    settings = await get_project_settings()
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    AsyncSessionMaker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    role_info = {
        "id": uuid4(),
        "name": settings.SUPER_ROLE_NAME,
        "permissions": [],
    }
    await create_role_in_database(role_info)

    async with AsyncSessionMaker() as isolated_session:
        assert (
            await check_creation_super_role(settings.SUPER_ROLE_NAME, isolated_session)
            == role_info["id"]
        )


async def test_check_creation_super_role_returns_none(get_project_settings):
    settings = await get_project_settings()
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    AsyncSessionMaker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionMaker() as isolated_session:
        assert (
            await check_creation_super_role(settings.SUPER_ROLE_NAME, isolated_session)
            is None
        )


@pytest.mark.asyncio
async def test_create_superadmin_creates_user_and_role(
    get_project_settings, get_user_from_database, get_user_id_by_username_from_database
):
    settings = await get_project_settings()
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    AsyncSessionMaker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    user_info = {
        "username": "admin",
        "password": "StrongPass1!",
        "first_name": "Admin",
        "last_name": "Super",
    }
    username = "admin"
    async with AsyncSessionMaker() as isolated_session:
        await create_superadmin(
            user_info["username"],
            user_info["password"],
            user_info["first_name"],
            user_info["last_name"],
            isolated_session,
        )

    user_id = await get_user_id_by_username_from_database(username)

    user_from_db: dict[str, Any] = await get_user_from_database(user_id)
    assert user_from_db["username"] == user_info["username"]
    assert user_from_db["first_name"] == user_info["first_name"]
    assert user_from_db["last_name"] == user_info["last_name"]
    assert user_from_db["patronymic"] is None
    assert user_from_db["employee_number"] is None
    assert len(user_from_db["roles"]) == 1
    assert user_from_db["roles"][0]["name"] == settings.SUPER_ROLE_NAME
