import pytest
from uuid import uuid4
from config.permissions import Permissions
from tests.conftest import DEVICE_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_update_device_name_success(
    client, create_device_in_database, get_device_from_database
):
    device_id = uuid4()
    original = {
        "id": device_id,
        "name": "test device",
        "android_id": "a3f9c2b7d18e44fa",
    }
    await create_device_in_database(original)

    body = {"name": "new name"}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}", json=body, headers=headers
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "new name"
    assert data["id"] == str(device_id)

    device_from_db = await get_device_from_database(device_id)
    assert device_from_db["name"] == "new name"


async def test_update_device_android_id_success(
    client, create_device_in_database, get_device_from_database
):
    device_id = uuid4()
    original = {
        "id": device_id,
        "name": "test device",
        "android_id": "a3f9c2b7d18e44fa",
    }
    await create_device_in_database(original)

    body = {"android_id": "new_android_id_12345"}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}", json=body, headers=headers
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["android_id"] == "new_android_id_12345"

    device_from_db = await get_device_from_database(device_id)
    assert device_from_db["android_id"] == "new_android_id_12345"


async def test_update_device_both_name_and_android_id(
    client, create_device_in_database, get_device_from_database
):
    device_id = uuid4()
    original = {
        "id": device_id,
        "name": "old name",
        "android_id": "old_android_id",
    }
    await create_device_in_database(original)

    body = {"name": "updated name", "android_id": "updated_android_id"}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}", json=body, headers=headers
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == body["name"]
    assert data["android_id"] == body["android_id"]

    device_from_db = await get_device_from_database(device_id)
    assert device_from_db["name"] == body["name"]
    assert device_from_db["android_id"] == body["android_id"]


@pytest.mark.parametrize(
    "existing, new",
    [("Device1", "device1"), ("MyDevice", "MYDEVICE"), ("TestDevice", "testdevice")],
)
async def test_update_device_duplicate_name_case_insensitive(
    client, create_device_in_database, existing, new
):
    first_id = uuid4()
    second_id = uuid4()

    await create_device_in_database(
        {
            "id": first_id,
            "name": existing,
            "android_id": "android1",
        }
    )

    await create_device_in_database(
        {
            "id": second_id,
            "name": "other device",
            "android_id": "android2",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{second_id}", json={"name": new}, headers=headers
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": f"Device with name {new} already exists."}


async def test_update_device_duplicate_android_id(client, create_device_in_database):
    first_id = uuid4()
    second_id = uuid4()

    await create_device_in_database(
        {
            "id": first_id,
            "name": "device1",
            "android_id": "android123",
        }
    )

    await create_device_in_database(
        {
            "id": second_id,
            "name": "device2",
            "android_id": "android456",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{second_id}",
        json={"android_id": "android123"},
        headers=headers,
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": "Device with this android_id already exists"}


async def test_update_device_not_found(client, create_device_in_database):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "existing device",
            "android_id": "android123",
        }
    )

    non_existent_id = uuid4()
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{non_existent_id}",
        json={"name": "new name"},
        headers=headers,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Device with this id not found"}


async def test_update_device_unauth(
    client, create_device_in_database, get_project_settings
):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "test device",
            "android_id": "android123",
        }
    )

    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}", json={"name": "new name"}
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_update_device_no_permission(
    client, create_device_in_database, get_project_settings
):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "test device",
            "android_id": "android123",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        json={"name": "new name"},
        headers=headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


@pytest.mark.parametrize(
    "bad_id, expected_status_code",
    [
        ("123", 422),
        ("not-uuid", 422),
        ("", 405),
        (" ", 422),
    ],
)
async def test_update_device_invalid_id(client, bad_id, expected_status_code):
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{bad_id}",
        json={"name": "new name"},
        headers=headers,
    )

    assert resp.status_code == expected_status_code


async def test_update_device_empty_body(client, create_device_in_database):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "test device",
            "android_id": "android123",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}", json={}, headers=headers
    )

    assert resp.status_code == 422
    assert resp.json() == {"detail": "At least one parameter must be defined"}


async def test_update_device_invalid_name_type(client, create_device_in_database):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "test device",
            "android_id": "android123",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        json={"name": 123},  # Invalid type - should be string
        headers=headers,
    )

    assert resp.status_code == 422


async def test_update_device_invalid_android_id_type(client, create_device_in_database):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "test device",
            "android_id": "android123",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        json={"android_id": 123},  # Invalid type - should be string
        headers=headers,
    )

    assert resp.status_code == 422


async def test_update_device_name_too_long(client, create_device_in_database):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "test device",
            "android_id": "android123",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        json={"name": "a" * 256},
        headers=headers,
    )

    assert resp.status_code == 422


async def test_update_device_android_id_too_long(client, create_device_in_database):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "test device",
            "android_id": "android123",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        json={"android_id": "a" * 256},
        headers=headers,
    )

    assert resp.status_code == 422


async def test_update_device_sql_injection_in_name(client, create_device_in_database):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "test device",
            "android_id": "android123",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    malicious = "'; DROP TABLE devices; --"
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        json={"name": malicious},
        headers=headers,
    )

    assert resp.status_code == 200


async def test_update_device_sql_injection_in_android_id(
    client, create_device_in_database
):
    device_id = uuid4()
    await create_device_in_database(
        {
            "id": device_id,
            "name": "test device",
            "android_id": "android123",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    malicious = "'; DROP TABLE devices; --"
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}",
        json={"android_id": malicious},
        headers=headers,
    )

    assert resp.status_code == 200


async def test_update_device_partial_success_when_other_field_unchanged(
    client, create_device_in_database, get_device_from_database
):
    device_id = uuid4()
    original_name = "original name"
    original_android_id = "original_android_id"

    original = {
        "id": device_id,
        "name": original_name,
        "android_id": original_android_id,
    }
    await create_device_in_database(original)

    body = {"name": "updated name"}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEVICE])
    resp = client.patch(
        f"{VERSION_URL}{DEVICE_URL}/{device_id}", json=body, headers=headers
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "updated name"
    assert data["android_id"] == original_android_id

    device_from_db = await get_device_from_database(device_id)
    assert device_from_db["name"] == "updated name"
    assert device_from_db["android_id"] == original_android_id
