from typing import Any
from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import USER_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_create_user_success(
    client, get_user_from_database, create_role_in_database
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    user_data = {
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "finger_token": "some_token123",
        "password": "StrongPass123!",
        "role_ids": [str(role_id)],
    }

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json=user_data,
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == user_data["username"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert data["patronymic"] == user_data["patronymic"]
    assert data["finger_token"] == user_data["finger_token"]
    assert data["role_ids"] == [str(role_id)]

    user_from_db: dict[str, Any] = await get_user_from_database(data["id"])
    assert user_from_db["username"] == user_data["username"]
    assert user_from_db["first_name"] == user_data["first_name"]
    assert user_from_db["last_name"] == user_data["last_name"]
    assert user_from_db["patronymic"] == user_data["patronymic"]
    assert user_from_db["finger_token"] == user_data["finger_token"]
    assert user_from_db["role_ids"] == [role_id]


@pytest.mark.parametrize(
    "existing,new",
    [
        ("JohnDoe", "johndoe"),
        ("TESTUSER", "testuser"),
        ("MiXeDCase", "mixedcase"),
    ],
)
async def test_create_user_duplicate_username_case_insensitive(
    client, create_user_in_database, existing, new
):
    await create_user_in_database(
        {
            "id": uuid4(),
            "username": existing,
            "first_name": "x",
            "last_name": "y",
            "password": "StrongPass123!",
        }
    )

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": new,
            "first_name": "A",
            "last_name": "B",
            "password": "StrongPass123!",
        },
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": f"User with username {new} already exists"}


@pytest.mark.parametrize(
    "password",
    ["", "short", "123", "abcdef", None],
)
async def test_create_user_invalid_password(client, password):
    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "abc",
            "first_name": "A",
            "last_name": "B",
            "password": password,
        },
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )
    assert resp.status_code == 422
    assert "password" in str(resp.json()).lower()


async def test_create_user_role_not_found(client):
    missing = uuid4()
    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "newperson",
            "first_name": "A",
            "last_name": "B",
            "password": "StrongPass123!",
            "role_ids": [str(missing)],
        },
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": f"Role with id {missing} not found"}


async def test_create_user_not_authenticated(client, get_project_settings):
    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "test",
            "first_name": "A",
            "last_name": "B",
            "password": "Pass123!",
        },
    )
    settings = await get_project_settings()

    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_create_user_bad_token(client, get_project_settings):
    headers = await create_auth_headers_for_user([Permissions.CREATE_USER])
    bad = {k: v + "broken" for k, v in headers.items()}
    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "test",
            "first_name": "A",
            "last_name": "B",
            "password": "Pass123!",
        },
        headers=bad,
    )
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_create_user_no_permission(client, get_project_settings):
    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "test",
            "first_name": "A",
            "last_name": "B",
            "password": "Pass123!",
        },
        headers=await create_auth_headers_for_user([Permissions.GET_USERS]),
    )
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


@pytest.mark.parametrize(
    "body, expected_missing",
    [
        ({}, ["username", "first_name", "last_name"]),
        ({"username": "a"}, ["first_name", "last_name"]),
        ({"first_name": "A", "last_name": "B"}, ["username"]),
        (
            {
                "username": "",
                "first_name": "A",
                "last_name": "B",
                "password": "StrongPass123!",
            },
            ["username"],
        ),
        (
            {
                "username": "test",
                "first_name": "",
                "last_name": "B",
                "password": "StrongPass123!",
            },
            ["first_name"],
        ),
        (
            {
                "username": "test",
                "first_name": "A",
                "last_name": "",
                "password": "StrongPass123!",
            },
            ["last_name"],
        ),
        (
            {"username": "test", "first_name": "A", "last_name": "B", "password": ""},
            ["password"],
        ),
    ],
)
async def test_create_user_validation(client, body, expected_missing):
    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json=body,
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )
    assert resp.status_code == 422
    error = str(resp.json())
    for f in expected_missing:
        assert f in error, f"Field '{f}' is missing in error: {error}"


async def test_create_user_super_admin_not_allowed(
    client, create_role_in_database, get_project_settings
):
    role_id = uuid4()
    settings = await get_project_settings()
    await create_role_in_database(
        {"id": role_id, "name": settings.SUPER_ROLE_NAME, "permissions": []}
    )

    user_data = {
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "password": "StrongPass123!",
        "role_ids": [str(role_id)],
    }

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json=user_data,
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )

    assert resp.status_code == 403
    assert resp.json() == {"detail": "Creating a superuser is forbidden"}
