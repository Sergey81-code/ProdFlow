import json
from typing import Any
from uuid import uuid4
import pytest

from config.permissions import Permissions
from tests.conftest import DEVICE_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_delete_device(
    client, create_device_in_database, get_device_from_database
):
    device_id = uuid4()
    device_info = {
        "id": device_id,
        "name": "test device",
        "android_id": "a3f9c2b7d18e44fa",
    }

    await create_device_in_database(device_info)
    headers_for_auth = await create_auth_headers_for_user([Permissions.DELETE_DEVICE])

    resp = client.delete(
        url=f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        headers=headers_for_auth,
    )
    assert resp.status_code == 200
    assert resp.json() == str(device_id)

    device_from_db: dict[str, Any] | None = await get_device_from_database(device_id)
    assert device_from_db is None


async def test_delete_device_not_found(client):
    non_existing_id = uuid4()
    headers_for_auth = await create_auth_headers_for_user([Permissions.DELETE_DEVICE])

    resp = client.delete(
        url=f"{VERSION_URL}{DEVICE_URL}/{non_existing_id}",
        headers=headers_for_auth,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Device with this id not found"}


async def test_delete_device_unauth(
    client, create_device_in_database, get_project_settings
):
    device_id = uuid4()
    await create_device_in_database(
        {"id": device_id, "name": "Unauth Device", "android_id": "a4f9c2b7d18e44fa"}
    )

    bad_headers = {"Authorization": "Bearer wrongtoken"}

    resp = client.delete(
        url=f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_delete_device_no_permissions(
    client, create_device_in_database, get_project_settings
):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "No Permission Device",
            "android_id": "a5f9c2b7d18e44fa",
        }
    )

    headers_for_auth = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.delete(
        url=f"{VERSION_URL}{DEVICE_URL}/{device_id}",
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
                        "loc": ["path", "device_id"],
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
                        "loc": ["path", "device_id"],
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
async def test_delete_device_invalid_id(
    client, bad_id, expected_status_code, expected_detail
):
    headers_for_auth = await create_auth_headers_for_user([Permissions.DELETE_DEVICE])

    resp = client.delete(
        url=f"{VERSION_URL}{DEVICE_URL}/{bad_id}",
        headers=headers_for_auth,
    )

    assert resp.status_code == expected_status_code
    assert resp.json() == expected_detail


async def test_delete_device_bad_credentials(
    client, create_device_in_database, get_project_settings
):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "Bad cred test device",
            "android_id": "a7f9c2b7d18e44fa",
        }
    )

    bad_headers = {"Authorization": "Bearer 111"}

    resp = client.delete(
        url=f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200
