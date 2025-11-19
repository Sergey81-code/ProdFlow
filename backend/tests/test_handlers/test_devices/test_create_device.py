from typing import Any
from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import DEVICE_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_create_device(client, get_device_from_database):
    device_info = {"name": "test device", "android_id": "a3f9c2b7d18e44fa"}

    resp = client.post(
        f"{VERSION_URL}{DEVICE_URL}/",
        json=device_info,
        headers=await create_auth_headers_for_user([Permissions.CREATE_DEVICE]),
    )

    assert resp.status_code == 200
    data_from_resp = resp.json()

    assert data_from_resp["name"] == device_info["name"]
    assert data_from_resp["android_id"] == device_info["android_id"]

    role_from_db: dict[str, Any] = await get_device_from_database(data_from_resp["id"])

    assert role_from_db["name"] == device_info["name"]
    assert role_from_db["android_id"] == device_info["android_id"]


@pytest.mark.parametrize(
    "existing_name,new_name",
    [
        ("Test Device", "test device"),
        ("TeSt DeViCe", "TEST DEVICE"),
        ("another name", "Another Name"),
    ],
)
async def test_create_device_duplicate_name_case_insensitive(
    client, create_device_in_database, existing_name, new_name
):
    await create_device_in_database(
        {"id": uuid4(), "name": existing_name, "android_id": "a3f9c2b7d18e44fa"}
    )

    resp = client.post(
        f"{VERSION_URL}{DEVICE_URL}/",
        json={"name": new_name, "android_id": "a4f9c2b7d18e44fa"},
        headers=await create_auth_headers_for_user([Permissions.CREATE_DEVICE]),
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": f"Device with name {new_name} already exists"}


@pytest.mark.parametrize(
    "existing,new,device_name",
    [
        ("A3F9C2B7D18E44FA", "a3f9c2b7d18e44fa", "New Device 1"),
        ("a3f9c2b7d18e44fa", "A3F9C2B7D18E44FA", "New Device 2"),
        ("A3f9C2b7D18E44Fa", "a3f9c2b7d18e44fa", "New Device 3"),
    ],
)
async def test_create_device_duplicate_android_id_case_insensitive(
    client, create_device_in_database, existing, new, device_name
):
    await create_device_in_database(
        {"id": uuid4(), "name": "Existing", "android_id": existing}
    )

    resp = client.post(
        f"{VERSION_URL}{DEVICE_URL}/",
        json={"name": device_name, "android_id": new},
        headers=await create_auth_headers_for_user([Permissions.CREATE_DEVICE]),
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": f"Device with android_id {new} already exists"}


async def test_create_device_not_authenticated(client, get_project_settings):
    resp = client.post(
        f"{VERSION_URL}{DEVICE_URL}/",
        json={"name": "Test", "android_id": "1234abcd"},
    )
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_create_device_bad_token(client, get_project_settings):
    headers = await create_auth_headers_for_user([Permissions.CREATE_DEVICE])
    bad_headers = {k: v + "broken" for k, v in headers.items()}

    resp = client.post(
        f"{VERSION_URL}{DEVICE_URL}/",
        json={"name": "Test", "android_id": "zz11"},
        headers=bad_headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_create_device_no_permission(client, get_project_settings):
    resp = client.post(
        f"{VERSION_URL}{DEVICE_URL}/",
        json={"name": "Test", "android_id": "abcd"},
        headers=await create_auth_headers_for_user([Permissions.GET_DEVICES]),
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
        ({}, ["name", "android_id"]),
        ({"name": "Test"}, ["android_id"]),
        ({"android_id": "a3f9c2b7d18e44fa"}, ["name"]),
        ({"name": None, "android_id": "a4f9c2b7d18e44fa"}, ["name"]),
        ({"name": "Test Device1", "android_id": None}, ["android_id"]),
        ({"name": "", "android_id": "a5f9c2b7d18e44fa"}, ["name"]),
        ({"name": "Test Device2", "android_id": ""}, ["android_id"]),
        ({"name": 123, "android_id": "a6f9c2b7d18e44fa"}, ["name"]),
        ({"name": "Test Device3", "android_id": 12345}, ["android_id"]),
        ({"name": "", "android_id": None}, ["android_id"]),
    ],
)
async def test_create_device_validation(client, body, expected_missing):
    resp = client.post(
        f"{VERSION_URL}{DEVICE_URL}/",
        json=body,
        headers=await create_auth_headers_for_user([Permissions.CREATE_DEVICE]),
    )

    assert resp.status_code == 422
    error_text = str(resp.json())
    for field in expected_missing:
        assert field in error_text, f"Field '{field}' not found in error: {error_text}"
