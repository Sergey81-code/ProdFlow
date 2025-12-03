from typing import Any
from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import USER_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_create_user_success(
    client,
    get_user_from_database,
    create_role_in_database,
    create_department_in_database,
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    department_id = uuid4()
    await create_department_in_database(
        {
            "id": department_id,
            "name": "test department name",
            "code": "some department code",
        }
    )

    user_data = {
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "employee_number": "some_token123",
        "password": "StrongPass123!",
        "role_ids": [str(role_id)],
        "department_id": str(department_id),
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
    assert data["employee_number"] == user_data["employee_number"]
    assert data["department_id"] == user_data["department_id"]
    assert [str(role_id)] == [role["id"] for role in data["roles"]]

    user_from_db: dict[str, Any] = await get_user_from_database(data["id"])
    assert user_from_db["username"] == user_data["username"]
    assert user_from_db["first_name"] == user_data["first_name"]
    assert user_from_db["last_name"] == user_data["last_name"]
    assert user_from_db["patronymic"] == user_data["patronymic"]
    assert user_from_db["employee_number"] == user_data["employee_number"]
    assert str(user_from_db["department_id"]) == user_data["department_id"]
    assert set([role_id]) == set([role["id"] for role in user_from_db["roles"]])


@pytest.mark.parametrize(
    "existing,new",
    [
        ("JohnDoe", "johndoe"),
        ("TESTUSER", "testuser"),
        ("MiXeDCase", "mixedcase"),
    ],
)
async def test_create_user_duplicate_username_case_insensitive(
    client,
    create_user_in_database,
    create_role_in_database,
    create_department_in_database,
    existing,
    new,
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    department_id = uuid4()
    await create_department_in_database(
        {"id": department_id, "name": "dep", "code": "D"}
    )

    await create_user_in_database(
        {
            "id": uuid4(),
            "username": existing,
            "first_name": "x",
            "last_name": "y",
            "password": "StrongPass123!",
            "department_id": department_id,
        }
    )

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": new,
            "first_name": "A",
            "last_name": "B",
            "password": "StrongPass123!",
            "role_ids": [str(role_id)],
            "department_id": str(department_id),
        },
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": f"User with username {new} already exists"}


@pytest.mark.parametrize(
    "password",
    ["", "short", "123", "abcdef", None],
)
async def test_create_user_invalid_password(
    client, password, create_role_in_database, create_department_in_database
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    department_id = uuid4()
    await create_department_in_database(
        {"id": department_id, "name": "test", "code": "X"}
    )

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "abc",
            "first_name": "A",
            "last_name": "B",
            "password": password,
            "role_ids": [str(role_id)],
            "department_id": str(department_id),
        },
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )
    assert resp.status_code == 422
    assert "password" in str(resp.json()).lower()


async def test_create_user_role_not_found(client, create_department_in_database):
    missing = uuid4()

    department_id = uuid4()
    await create_department_in_database(
        {"id": department_id, "name": "test", "code": "Z"}
    )

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "newperson",
            "first_name": "A",
            "last_name": "B",
            "password": "StrongPass123!",
            "role_ids": [str(missing)],
            "department_id": str(department_id),
        },
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": f"Role with id {missing} not found"}


async def test_create_user_not_authenticated(
    client, get_project_settings, create_department_in_database
):
    department_id = uuid4()
    await create_department_in_database({"id": department_id, "name": "T", "code": "C"})

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "test",
            "first_name": "A",
            "last_name": "B",
            "password": "Pass123!",
            "department_id": str(department_id),
        },
    )
    settings = await get_project_settings()

    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_create_user_bad_token(
    client, get_project_settings, create_role_in_database, create_department_in_database
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    department_id = uuid4()
    await create_department_in_database({"id": department_id, "name": "A", "code": "B"})

    headers = await create_auth_headers_for_user([Permissions.CREATE_USER])
    bad = {k: v + "broken" for k, v in headers.items()}

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "test",
            "first_name": "A",
            "last_name": "B",
            "password": "Pass123!",
            "role_ids": [str(role_id)],
            "department_id": str(department_id),
        },
        headers=bad,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_create_user_no_permission(
    client, get_project_settings, create_role_in_database, create_department_in_database
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    department_id = uuid4()
    await create_department_in_database({"id": department_id, "name": "A", "code": "B"})

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "test",
            "first_name": "A",
            "last_name": "B",
            "password": "Pass123!",
            "role_ids": [str(role_id)],
            "department_id": str(department_id),
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
        ({}, ["username", "first_name", "last_name", "department_id"]),
        ({"username": "a"}, ["first_name", "last_name", "department_id"]),
        ({"first_name": "A", "last_name": "B"}, ["username"]),
        (
            {"username": "", "first_name": "A", "last_name": "B", "password": "Strong"},
            ["username"],
        ),
        (
            {
                "username": "test",
                "first_name": "",
                "last_name": "B",
                "password": "Strong",
            },
            ["first_name"],
        ),
        (
            {
                "username": "test",
                "first_name": "A",
                "last_name": "",
                "password": "Strong",
            },
            ["last_name"],
        ),
        (
            {"username": "test", "first_name": "A", "last_name": "B", "password": ""},
            ["password"],
        ),
    ],
)
async def test_create_user_validation(
    client,
    body,
    expected_missing,
    create_role_in_database,
    create_department_in_database,
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    # всегда добавляем корректный department_id если его нет
    department_id = uuid4()
    await create_department_in_database({"id": department_id, "name": "D", "code": "X"})

    body = {
        **body,
        "role_ids": [str(role_id)],
        **(
            {"department_id": str(department_id)} if "department_id" not in body else {}
        ),
    }

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json=body,
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )

    assert resp.status_code == 422
    error = str(resp.json())
    for f in expected_missing:
        assert f in error


async def test_create_user_super_admin_not_allowed(
    client, create_role_in_database, create_department_in_database, get_project_settings
):
    role_id = uuid4()
    settings = await get_project_settings()

    await create_role_in_database(
        {"id": role_id, "name": settings.SUPER_ROLE_NAME, "permissions": []}
    )

    department_id = uuid4()
    await create_department_in_database({"id": department_id, "name": "X", "code": "Y"})

    user_data = {
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "password": "StrongPass123!",
        "role_ids": [str(role_id)],
        "department_id": str(department_id),
    }

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json=user_data,
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )

    assert resp.status_code == 403
    assert resp.json() == {"detail": "Creating a superuser is forbidden"}


@pytest.mark.parametrize("dep", ["", "not-uuid", 123])
async def test_create_user_invalid_department_id(client, dep, create_role_in_database):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "abc",
            "first_name": "A",
            "last_name": "B",
            "password": "Pass123!",
            "role_ids": [str(role_id)],
            "department_id": dep,
        },
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )

    assert resp.status_code == 422
    assert "department_id" in str(resp.json()).lower()


async def test_create_user_department_not_found(client, create_role_in_database):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    missing_dep = uuid4()

    resp = client.post(
        f"{VERSION_URL}{USER_URL}/",
        json={
            "username": "abc",
            "first_name": "A",
            "last_name": "B",
            "password": "Pass123!",
            "role_ids": [str(role_id)],
            "department_id": str(missing_dep),
        },
        headers=await create_auth_headers_for_user([Permissions.CREATE_USER]),
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": f"Department with id {missing_dep} not found"}
