from typing import Any
from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import ROLE_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user

from typing import Any
from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import ROLE_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_delete_role_success(
    client,
    create_user_in_database,
    create_role_in_database,
    get_role_from_database,
    get_user_from_database,
):
    role_id = uuid4()
    role_id_not_deleted = uuid4()

    user_info1 = {
        "id": uuid4(),
        "username": "johndoe1",
        "first_name": "John1",
        "last_name": "Doe1",
        "patronymic": "Martin1",
        "employee_number": "some_token123",
        "role_ids": [role_id, role_id_not_deleted],
    }
    user_info2 = {
        "id": uuid4(),
        "username": "johndoe2",
        "first_name": "John2",
        "last_name": "Doe2",
        "patronymic": "Martin2",
        "employee_number": "some_token13",
        "role_ids": [role_id, role_id_not_deleted],
    }
    role1_info = {
        "id": role_id,
        "name": "test role1",
        "permissions": [Permissions.CREATE_DEVICE],
    }
    role2_info = {
        "id": role_id_not_deleted,
        "name": "test role2",
        "permissions": [Permissions.CREATE_DEVICE],
    }
    await create_role_in_database(role1_info)
    await create_role_in_database(role2_info)
    await create_user_in_database(user_info1)
    await create_user_in_database(user_info2)

    headers = await create_auth_headers_for_user([Permissions.DELETE_ROLE])

    resp = client.delete(
        url=f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers=headers,
    )

    assert resp.status_code == 200
    assert resp.json() == str(role_id)

    role_from_db = await get_role_from_database(role_id)
    assert role_from_db is None

    user1_from_db = await get_user_from_database(user_info1["id"])
    user2_from_db = await get_user_from_database(user_info2["id"])

    assert role_id not in [role["id"] for role in user1_from_db["roles"]]
    assert role_id not in [role["id"] for role in user2_from_db["roles"]]


async def test_delete_role_not_found(client):
    headers = await create_auth_headers_for_user([Permissions.DELETE_ROLE])
    non_existing_id = uuid4()

    resp = client.delete(f"{VERSION_URL}{ROLE_URL}/{non_existing_id}", headers=headers)

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Role with this id not found"}


async def test_delete_role_unauth(
    client, create_role_in_database, get_project_settings
):
    role_id = uuid4()
    role_info = {
        "id": role_id,
        "name": "unauth role",
        "permissions": [Permissions.GET_DEVICES],
    }
    await create_role_in_database(role_info)

    resp = client.delete(
        f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers={"Authorization": "Bearer wrongtoken"},
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_delete_role_no_permissions(
    client, create_role_in_database, get_project_settings
):
    role_id = uuid4()
    role_info = {
        "id": role_id,
        "name": "no perm role",
        "permissions": [Permissions.GET_DEVICES],
    }
    await create_role_in_database(role_info)

    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.delete(f"{VERSION_URL}{ROLE_URL}/{role_id}", headers=headers)

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


@pytest.mark.parametrize(
    "bad_id, expected_status_code, expected_detail",
    [
        (
            "123",
            422,
            {
                "detail": [
                    {
                        "type": "uuid_parsing",
                        "loc": ["path", "role_id"],
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
            422,
            {
                "detail": [
                    {
                        "type": "uuid_parsing",
                        "loc": ["path", "role_id"],
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
async def test_delete_role_invalid_id(
    client, bad_id, expected_status_code, expected_detail
):
    headers = await create_auth_headers_for_user([Permissions.DELETE_ROLE])

    resp = client.delete(f"{VERSION_URL}{ROLE_URL}/{bad_id}", headers=headers)

    assert resp.status_code == expected_status_code
    assert resp.json() == expected_detail


async def test_delete_role_bad_credentials(
    client, create_role_in_database, get_project_settings
):
    role_id = uuid4()
    role_info = {
        "id": role_id,
        "name": "bad cred role",
        "permissions": [Permissions.GET_DEVICES],
    }
    await create_role_in_database(role_info)

    resp = client.delete(
        f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers={"Authorization": "Bearer 111"},
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_delete_role_super_admin_not_allowed(
    client, create_role_in_database, get_project_settings
):
    role_id = uuid4()
    settings = await get_project_settings()
    role_info = {
        "id": role_id,
        "name": settings.SUPER_ROLE_NAME,
        "permissions": [Permissions.GET_DEVICES],
    }

    await create_role_in_database(role_info)

    headers = await create_auth_headers_for_user([Permissions.DELETE_ROLE])

    resp = client.delete(f"{VERSION_URL}{ROLE_URL}/{role_id}", headers=headers)

    assert resp.status_code == 403
    assert resp.json() == {"detail": "Super role is not allowed to perform this action"}
