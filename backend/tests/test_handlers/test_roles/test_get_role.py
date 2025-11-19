import pytest
from uuid import uuid4
from config.permissions import Permissions
from tests.conftest import ROLE_URL, VERSION_URL
from tests.utils_for_tests import _create_roles, create_auth_headers_for_user


async def test_get_role(client, create_role_in_database, get_role_from_database):
    role_id = uuid4()
    role_info = {
        "id": role_id,
        "name": "test role",
        "permissions": [
            Permissions.CREATE_DEVICE,
            Permissions.DELETE_DEVICE,
        ],
    }

    await create_role_in_database(role_info)
    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(
        url=f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(role_id)
    assert data["name"] == role_info["name"]
    assert data["permissions"] == role_info["permissions"]

    role_from_database = await get_role_from_database(role_id)
    assert role_from_database["name"] == role_info["name"]
    assert role_from_database["permissions"] == role_info["permissions"]


async def test_get_role_not_found(client):
    non_existing_id = uuid4()
    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(
        url=f"{VERSION_URL}{ROLE_URL}/{non_existing_id}",
        headers=headers,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Role with this id not found"}


async def test_get_role_unauth(client, create_role_in_database, get_project_settings):
    role_id = uuid4()
    role_info = {
        "id": role_id,
        "name": "test role",
        "permissions": [
            Permissions.CREATE_DEVICE,
            Permissions.DELETE_DEVICE,
        ],
    }

    await create_role_in_database(role_info)

    bad_headers = {"Authorization": "Bearer wrongtoken"}

    resp = client.get(
        url=f"{VERSION_URL}{ROLE_URL}/{role_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_get_role_no_permissions(
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

    resp = client.get(
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
async def test_get_role_invalid_id(
    client, create_role_in_database, bad_id, expected_status_code, expected_detail
):
    role_id = uuid4()
    role_info = {
        "id": role_id,
        "name": "no permission role",
        "permissions": [Permissions.GET_DEVICES],
    }
    await create_role_in_database(role_info)

    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])
    resp = client.get(url=f"{VERSION_URL}{ROLE_URL}/{bad_id}", headers=headers)
    assert resp.status_code == expected_status_code
    assert resp.json() == expected_detail


async def test_get_all_roles(client, create_role_in_database):
    roles = await _create_roles(create_role_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(f"{VERSION_URL}{ROLE_URL}/", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == len(roles)


async def test_get_roles_by_name_exact_match(client, create_role_in_database):
    await _create_roles(create_role_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(f"{VERSION_URL}{ROLE_URL}/?role_name=Admin", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Admin"


async def test_get_roles_by_name_case_insensitive(client, create_role_in_database):
    await _create_roles(create_role_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(f"{VERSION_URL}{ROLE_URL}/?role_name=admIN", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Admin"


async def test_get_roles_by_name_partial_match(client, create_role_in_database):
    await _create_roles(create_role_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(f"{VERSION_URL}{ROLE_URL}/?role_name=ser", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "SuperUser"


async def test_get_roles_no_results(client, create_role_in_database):
    await _create_roles(create_role_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(f"{VERSION_URL}{ROLE_URL}/?role_name=unknown", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data == []


async def test_get_roles_empty_query_returns_all(client, create_role_in_database):
    roles = await _create_roles(create_role_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(f"{VERSION_URL}{ROLE_URL}/?role_name=", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == len(roles)


async def test_get_roles_unauthorized_no_token(
    client, create_role_in_database, get_project_settings
):
    await _create_roles(create_role_in_database)

    resp = client.get(f"{VERSION_URL}{ROLE_URL}/")

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_get_roles_forbidden(
    client, create_role_in_database, get_project_settings
):
    await _create_roles(create_role_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])

    resp = client.get(f"{VERSION_URL}{ROLE_URL}/", headers=headers)

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


async def test_get_roles_wrong_token(
    client, create_role_in_database, get_project_settings
):
    await _create_roles(create_role_in_database)

    resp = client.get(
        f"{VERSION_URL}{ROLE_URL}/",
        headers={"Authorization": "Bearer invalid"},
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200
