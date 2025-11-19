from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import USER_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_delete_user(
    client, create_role_in_database, create_user_in_database, get_user_from_database
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    user_data = {
        "id": uuid4(),
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "finger_token": "some_token123",
        "password": "StrongPass123!",
        "role_ids": [str(role_id)],
    }

    user_id = await create_user_in_database(user_data)

    headers_for_auth = await create_auth_headers_for_user([Permissions.DELETE_USER])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=headers_for_auth,
    )

    assert resp.status_code == 200
    assert resp.json() == str(user_id)

    user_from_db = await get_user_from_database(user_id)
    assert user_from_db is None


async def test_delete_user_not_found(client):
    non_existing_id = uuid4()
    headers = await create_auth_headers_for_user([Permissions.DELETE_USER])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{non_existing_id}",
        headers=headers,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "User with this id not found"}


@pytest.mark.parametrize(
    "bad_id, expected_detail",
    [
        (
            "123",
            {
                "detail": [
                    {
                        "type": "uuid_parsing",
                        "loc": ["path", "user_id"],
                        "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 3",
                        "input": "123",
                        "ctx": {
                            "error": "invalid length: expected length 32 for simple format, found 3"
                        },
                    }
                ]
            },
        ),
        (
            "not-a-uuid",
            {
                "detail": [
                    {
                        "type": "uuid_parsing",
                        "loc": ["path", "user_id"],
                        "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `n` at 1",
                        "input": "not-a-uuid",
                        "ctx": {
                            "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `n` at 1"
                        },
                    }
                ]
            },
        ),
    ],
)
async def test_delete_user_invalid_id(client, bad_id, expected_detail):
    headers = await create_auth_headers_for_user([Permissions.DELETE_USER])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{bad_id}",
        headers=headers,
    )

    assert resp.status_code == 422
    assert resp.json() == expected_detail


async def test_delete_user_unauth(
    client, create_role_in_database, create_user_in_database, get_project_settings
):
    role_id = uuid4()
    await create_role_in_database({"id": role_id, "name": "x", "permissions": []})

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "bad",
            "first_name": "Bad",
            "last_name": "Token",
            "patronymic": "Test",
            "finger_token": "tok",
            "password": "123",
            "role_ids": [str(role_id)],
        }
    )

    bad_headers = {"Authorization": "Bearer wrongtoken"}

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_delete_user_no_permissions(
    client, create_role_in_database, create_user_in_database, get_project_settings
):
    role_id = uuid4()
    await create_role_in_database({"id": role_id, "name": "x", "permissions": []})

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "noperms",
            "first_name": "No",
            "last_name": "Perms",
            "patronymic": "Test",
            "finger_token": "tok",
            "password": "123",
            "role_ids": [str(role_id)],
        }
    )

    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


async def test_delete_user_bad_credentials(
    client, create_role_in_database, create_user_in_database, get_project_settings
):
    role_id = uuid4()
    await create_role_in_database({"id": role_id, "name": "test", "permissions": []})

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "badcred",
            "first_name": "Bad",
            "last_name": "Cred",
            "patronymic": "Test",
            "finger_token": "tok",
            "password": "123",
            "role_ids": [str(role_id)],
        }
    )

    bad_headers = {"Authorization": "Bearer 111"}

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_delete_super_user_not_allowed(
    client,
    create_role_in_database,
    create_user_in_database,
    get_project_settings,
):
    settings = await get_project_settings()

    role_id = uuid4()
    await create_role_in_database(
        {
            "id": role_id,
            "name": settings.SUPER_ROLE_NAME,
            "permissions": [p for p in Permissions],
        }
    )

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "superuser",
            "first_name": "Super",
            "last_name": "Admin",
            "patronymic": "Test",
            "finger_token": "tok",
            "password": "123",
            "role_ids": [str(role_id)],
        }
    )

    headers = await create_auth_headers_for_user([Permissions.DELETE_USER])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=headers,
    )

    assert resp.status_code == 403
    assert resp.json() == {
        "detail": "User with super role is not allowed to perform this action"
    }
