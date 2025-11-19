import pytest
from uuid import uuid4
from config.permissions import Permissions
from tests.conftest import DEVICE_URL, VERSION_URL
from tests.utils_for_tests import _create_devices, create_auth_headers_for_user


async def test_get_device(client, create_device_in_database, get_device_from_database):
    device_id = uuid4()
    device_info = {"name": "test device", "android_id": "a3f9c2b7d18e44fa"}

    await create_device_in_database({"id": device_id, **device_info})
    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/{device_id}", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(device_id)
    assert data["name"] == device_info["name"]
    assert data["android_id"] == device_info["android_id"]

    device_from_db = await get_device_from_database(device_id)
    assert device_from_db["name"] == device_info["name"]
    assert device_from_db["android_id"] == device_info["android_id"]


async def test_get_device_not_found(client):
    non_existing_id = uuid4()
    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/{non_existing_id}", headers=headers)

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Device with this id not found"}


async def test_get_device_unauth(
    client, create_device_in_database, get_project_settings
):
    device_id = uuid4()
    device_info = {"name": "test device", "android_id": "a3f9c2b7d18e44fa"}
    await create_device_in_database({"id": device_id, **device_info})

    bad_headers = {"Authorization": "Bearer wrongtoken"}

    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/{device_id}", headers=bad_headers)
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_get_device_no_permissions(
    client, create_device_in_database, get_project_settings
):
    device_id = uuid4()
    device_info = {"name": "test device", "android_id": "a3f9c2b7d18e44fa"}
    await create_device_in_database({"id": device_id, **device_info})

    headers = await create_auth_headers_for_user([Permissions.CREATE_DEVICE])

    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/{device_id}", headers=headers)
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
async def test_get_device_invalid_id(
    client, create_device_in_database, bad_id, expected_status_code, expected_detail
):
    device_id = uuid4()
    device_info = {"name": "test device", "android_id": "a3f9c2b7d18e44fa"}
    await create_device_in_database({"id": device_id, **device_info})

    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])
    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/{bad_id}", headers=headers)
    assert resp.status_code == expected_status_code
    assert resp.json() == expected_detail


async def test_get_all_devices(client, create_device_in_database):
    devices = await _create_devices(create_device_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == len(devices)


async def test_get_devices_by_name_exact_match(client, create_device_in_database):
    await _create_devices(create_device_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.get(
        f"{VERSION_URL}{DEVICE_URL}/?device_name=Test Device 1", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Device 1"


async def test_get_devices_by_name_case_insensitive(client, create_device_in_database):
    await _create_devices(create_device_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.get(
        f"{VERSION_URL}{DEVICE_URL}/?device_name=tEsT deViCe 1", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Device 1"


async def test_get_devices_by_name_partial_match(client, create_device_in_database):
    await _create_devices(create_device_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/?device_name=Dev", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


async def test_get_devices_no_results(client, create_device_in_database):
    await _create_devices(create_device_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.get(
        f"{VERSION_URL}{DEVICE_URL}/?device_name=unknown", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


async def test_get_devices_empty_query_returns_all(client, create_device_in_database):
    devices = await _create_devices(create_device_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/?device_name=", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == len(devices)


async def test_get_devices_unauthorized_no_token(
    client, create_device_in_database, get_project_settings
):
    await _create_devices(create_device_in_database)

    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/")
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_get_devices_forbidden(
    client, create_device_in_database, get_project_settings
):
    await _create_devices(create_device_in_database)
    headers = await create_auth_headers_for_user([Permissions.CREATE_DEVICE])

    resp = client.get(f"{VERSION_URL}{DEVICE_URL}/", headers=headers)
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


async def test_get_devices_wrong_token(
    client, create_device_in_database, get_project_settings
):
    await _create_devices(create_device_in_database)

    resp = client.get(
        f"{VERSION_URL}{DEVICE_URL}/", headers={"Authorization": "Bearer invalid"}
    )
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200
