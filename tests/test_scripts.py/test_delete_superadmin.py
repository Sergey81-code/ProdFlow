from unittest.mock import patch
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.permissions import Permissions
from db.models import User
from scripts.delete_superadmin import delete_superadmin


async def test_delete_superadmin(
    create_user_in_database,
    create_role_in_database,
    get_project_settings,
):
    settings = await get_project_settings()
    role_id = uuid4()
    await create_role_in_database(
        {
            "id": role_id,
            "name": settings.SUPER_ROLE_NAME,
            "permissions": [permission for permission in Permissions],
        }
    )

    user_data = {
        "id": uuid4(),
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "employee_number": "some_token123",
        "password": "StrongPass123!",
        "role_ids": [str(role_id)],
    }

    await create_user_in_database(user_data)

    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    AsyncSessionMaker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionMaker() as isolated_session:
        await delete_superadmin(user_data["username"], isolated_session)
        await isolated_session.commit()

        result = await isolated_session.execute(
            select(User).where(User.username == user_data["username"])
        )
        users = result.unique().scalars().all()

    assert len(users) == 0


async def test_delete_superadmin_username_not_found(
    create_role_in_database,
    create_user_in_database,
    get_user_from_database,
    get_project_settings,
):
    settings = await get_project_settings()
    role_id = uuid4()
    await create_role_in_database(
        {
            "id": role_id,
            "name": settings.SUPER_ROLE_NAME,
            "permissions": [permission for permission in Permissions],
        }
    )

    user_data = {
        "id": uuid4(),
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "employee_number": "some_token123",
        "password": "StrongPass123!",
        "role_ids": [str(role_id)],
    }
    await create_user_in_database(user_data.copy())

    username_not_exists = "nonexistent@example.com"

    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    AsyncSessionMaker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionMaker() as isolated_session:
        with patch("builtins.print") as mock_print:
            await delete_superadmin(username_not_exists, isolated_session)
            mock_print.assert_any_call(
                "Error: A user with this username does not exist."
            )

    user_from_db = await get_user_from_database(user_data["id"])

    assert user_from_db["id"] == user_data["id"]
    assert user_from_db["first_name"] == user_data["first_name"]
    assert user_from_db["last_name"] == user_data["last_name"]
    assert user_from_db["patronymic"] == user_data["patronymic"]
    assert user_from_db["employee_number"] == user_data["employee_number"]
    assert user_from_db["password"] == user_data["password"]
    assert set(str(role["id"]) for role in user_from_db["roles"]) == set(
        user_data["role_ids"]
    )
