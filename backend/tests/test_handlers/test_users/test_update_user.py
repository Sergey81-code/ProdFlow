from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import USER_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_update_user(
    client, create_user_in_database, create_role_in_database, get_user_from_database
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "john",
            "first_name": "John",
            "last_name": "Doe",
            "patronymic": "M",
            "finger_token": "token123",
            "password": "Pass123!",
            "role_ids": [str(role_id)],
        }
    )

    body = {
        "username": "newjohn",
        "first_name": "Johnny",
        "last_name": "Doeman",
        "patronymic": "Martin",
        "finger_token": "new_token321",
        "password": "Pass12312!!",
        "role_ids": [str(role_id)],
    }

    headers = await create_auth_headers_for_user([Permissions.UPDATE_USER])

    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{user_id}",
        json=body,
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == body["username"]
    assert data["first_name"] == body["first_name"]
    assert data["last_name"] == body["last_name"]
    assert data["patronymic"] == body["patronymic"]
    assert data["finger_token"] == body["finger_token"]
    assert [str(role) for role in data["role_ids"]] == body["role_ids"]

    user_db = await get_user_from_database(user_id)
    assert user_db["username"] == body["username"]
    assert user_db["first_name"] == body["first_name"]
    assert user_db["last_name"] == body["last_name"]
    assert user_db["patronymic"] == body["patronymic"]
    assert [str(role) for role in user_db["role_ids"]] == body["role_ids"]


async def test_update_user_role_change_success(
    client, create_user_in_database, create_role_in_database, get_user_from_database
):
    rid_old = uuid4()
    rid_new = uuid4()

    await create_role_in_database(
        {"id": rid_old, "name": "employee", "permissions": []}
    )
    await create_role_in_database({"id": rid_new, "name": "manager", "permissions": []})

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "u",
            "first_name": "F",
            "last_name": "L",
            "patronymic": "P",
            "finger_token": "T",
            "password": "Pass123!",
            "role_ids": [str(rid_old)],
        }
    )

    body = {"role_ids": [str(rid_new)]}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_USER])

    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{user_id}", json=body, headers=headers
    )
    assert resp.status_code == 200

    user_db = await get_user_from_database(user_id)
    assert set(user_db["role_ids"]) == {rid_new}


async def test_update_user_forbidden_for_super(
    client, create_user_in_database, create_role_in_database, get_project_settings
):
    settings = await get_project_settings()

    super_role_id = uuid4()
    await create_role_in_database(
        {
            "id": super_role_id,
            "name": settings.SUPER_ROLE_NAME,
            "permissions": [],
        }
    )

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "superuser",
            "first_name": "A",
            "last_name": "B",
            "patronymic": "-",
            "finger_token": "x",
            "password": "Pass123!",
            "role_ids": [str(super_role_id)],
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_USER])

    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{user_id}",
        json={"first_name": "New"},
        headers=headers,
    )

    assert resp.status_code == 403
    assert resp.json() == {
        "detail": "User with super role is not allowed to perform this action"
    }


async def test_update_user_unauthenticated(
    client, create_user_in_database, get_project_settings
):
    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "u",
            "first_name": "F",
            "last_name": "L",
            "patronymic": "P",
            "finger_token": "T",
            "password": "Pass123!",
            "role_ids": [],
        }
    )

    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{user_id}",
        json={"first_name": "New"},
    )
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_update_user_no_permissions(
    client, create_user_in_database, get_project_settings
):
    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "u",
            "first_name": "F",
            "last_name": "L",
            "patronymic": "P",
            "finger_token": "T",
            "password": "Pass123!",
            "role_ids": [],
        }
    )

    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{user_id}",
        json={"first_name": "New"},
        headers=headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


@pytest.mark.parametrize(
    "bad_id, expected",
    [("x", 422), ("123", 422), ("", 405), ("  ", 422)],
)
async def test_update_user_invalid_id(client, bad_id, expected):
    headers = await create_auth_headers_for_user([Permissions.UPDATE_USER])
    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{bad_id}",
        json={"first_name": "X"},
        headers=headers,
    )
    assert resp.status_code == expected


async def test_update_user_empty_body(client, create_user_in_database):
    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "u",
            "first_name": "F",
            "last_name": "L",
            "patronymic": "P",
            "finger_token": "T",
            "password": "Pass123!",
            "role_ids": [],
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_USER])

    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{user_id}",
        json={},
        headers=headers,
    )

    assert resp.status_code == 422
    assert resp.json() == {"detail": "At least one parameter must be defined"}


async def test_update_user_invalid_role_ids_type(client, create_user_in_database):
    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "u",
            "first_name": "F",
            "last_name": "L",
            "patronymic": "P",
            "finger_token": "T",
            "password": "Pass123!",
            "role_ids": [],
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_USER])

    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{user_id}",
        json={"role_ids": "not-list"},
        headers=headers,
    )

    assert resp.status_code == 422


async def test_update_user_sql_injection(client, create_user_in_database):
    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "test",
            "first_name": "F",
            "last_name": "L",
            "patronymic": "P",
            "finger_token": "T",
            "password": "Pass123!",
            "role_ids": [],
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_USER])
    malicious = "'; DROP TABLE users; --"

    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{user_id}",
        json={"username": malicious},
        headers=headers,
    )

    assert resp.status_code == 200


@pytest.mark.parametrize(
    "body, expected_status, expected_error_fragment",
    [
        ({"username": ""}, 422, "Field cannot be empty"),
        ({"username": "   "}, 422, "Field cannot be empty"),
        ({"username": "very" * 100}, 422, "Field length must be <= 99 characters"),
        ({"first_name": ""}, 422, "Field cannot be empty"),
        ({"first_name": " "}, 422, "Field cannot be empty"),
        ({"first_name": "A" * 100}, 422, "Field length must be <= 99 characters"),
        ({"last_name": ""}, 422, "Field cannot be empty"),
        ({"last_name": " "}, 422, "Field cannot be empty"),
        ({"last_name": "A" * 200}, 422, "Field length must be <= 99 characters"),
        ({"patronymic": "A" * 200}, 422, "Field length must be <= 99 characters"),
        ({"finger_token": "x" * 100}, 422, "Field length must be <= 64 characters"),
        ({"password": "short"}, 422, "Password"),
        ({"password": "a" * 200}, 422, "Field length must be <= 99 characters"),
        ({"role_ids": "not-a-list"}, 422, "Input should be a valid list"),
        ({"role_ids": ["not-uuid"]}, 422, "Input should be a valid UUID"),
        (
            {"role_ids": [123]},
            422,
            "UUID input should be a string, bytes or UUID object",
        ),
        (
            {"role_ids": [None]},
            422,
            "UUID input should be a string, bytes or UUID object",
        ),
    ],
)
async def test_update_user_all_validation_errors(
    client,
    body,
    expected_status,
    expected_error_fragment,
    create_user_in_database,
):
    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "valid",
            "first_name": "John",
            "last_name": "Doe",
            "patronymic": "Michael",
            "finger_token": "abc123",
            "password": "ValidPass123!",
            "role_ids": [],
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_USER])

    resp = client.patch(
        f"{VERSION_URL}{USER_URL}/{user_id}",
        json=body,
        headers=headers,
    )

    assert resp.status_code == expected_status, resp.text
    assert expected_error_fragment in str(resp.json()), resp.json()
