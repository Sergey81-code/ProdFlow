import json
from typing import Any
from uuid import uuid4

import pytest
from config.permissions import Permissions
from tests.conftest import ROLE_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_delete_role(client, create_role_in_database, get_role_from_database):
    role_id = uuid4()
    role_info = {
        "id": role_id,
        "name": "test role",
        "permissions": [
            Permissions.CREATE_DEVICE,
            Permissions.DELETE_DEVICE,
            Permissions.GET_DEVICES,
            Permissions.UPDATE_DEVICE,
        ],
    }

    await create_role_in_database(role_info)

    headers_for_auth = await create_auth_headers_for_user([Permissions.DELETE_ROLE])

    resp = client.delete(
        url=f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers=headers_for_auth,
    )

    assert resp.status_code == 200
    data_from_resp = resp.json()

    assert data_from_resp == str(role_id)

    role_from_db: dict[str, Any] | None = await get_role_from_database(role_id)

    assert role_from_db is None


async def test_delete_role_not_found(client, create_role_in_database):
    non_existing_id = uuid4()
    headers_for_auth = await create_auth_headers_for_user([Permissions.DELETE_ROLE])

    resp = client.delete(
        url=f"{VERSION_URL}{ROLE_URL}/{non_existing_id}",
        headers=headers_for_auth,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Role with this id not found"}


async def test_delete_role_unauth(
    client, create_role_in_database, get_project_settings
):
    role_id = uuid4()
    role_info = {
        "id": role_id,
        "name": "unauth test role",
        "permissions": [Permissions.GET_DEVICES],
    }
    await create_role_in_database(role_info)

    bad_headers = {"Authorization": "Bearer wrongtoken"}

    resp = client.delete(
        url=f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers=bad_headers,
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
        "name": "no permission role",
        "permissions": [Permissions.GET_DEVICES],
    }
    await create_role_in_database(role_info)

    headers_for_auth = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.delete(
        url=f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers=headers_for_auth,
    )

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
    headers_for_auth = await create_auth_headers_for_user([Permissions.DELETE_ROLE])

    resp = client.delete(
        url=f"{VERSION_URL}{ROLE_URL}/{bad_id}",
        headers=headers_for_auth,
    )

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

    bad_headers = {"Authorization": "Bearer 111"}

    resp = client.delete(
        url=f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_delete_role_super_admin_not_allowed(
    client, create_role_in_database, get_role_from_database, get_project_settings
):
    role_id = uuid4()
    settings = await get_project_settings()
    role_info = {
        "id": role_id,
        "name": settings.SUPER_ROLE_NAME,
        "permissions": [
            Permissions.CREATE_DEVICE,
            Permissions.DELETE_DEVICE,
            Permissions.GET_DEVICES,
            Permissions.UPDATE_DEVICE,
        ],
    }

    await create_role_in_database(role_info)

    headers_for_auth = await create_auth_headers_for_user([Permissions.DELETE_ROLE])

    resp = client.delete(
        url=f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers=headers_for_auth,
    )

    assert resp.status_code == 403
    assert resp.json() == {"detail": "Super role is not allowed to perform this action"}
