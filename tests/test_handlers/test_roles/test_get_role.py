from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import ROLE_URL, VERSION_URL
from tests.utils_for_tests import _create_roles, create_auth_headers_for_user


async def test_get_role(
    client, create_user_in_database, create_role_in_database, get_role_from_database
):
    role_id = uuid4()
    user_info1 = {
        "id": uuid4(),
        "username": "johndoe1",
        "first_name": "John1",
        "last_name": "Doe1",
        "patronymic": "Martin1",
        "employee_number": "some_token123",
        "role_ids": [role_id],
    }
    user_info2 = {
        "id": uuid4(),
        "username": "johndoe2",
        "first_name": "John2",
        "last_name": "Doe2",
        "patronymic": "Martin2",
        "employee_number": "some_token13",
        "role_ids": [role_id],
    }

    role_info = {
        "id": role_id,
        "name": "test role",
        "permissions": [
            Permissions.CREATE_DEVICE,
            Permissions.DELETE_DEVICE,
        ],
    }

    await create_role_in_database(role_info)
    await create_user_in_database(user_info1)
    await create_user_in_database(user_info2)
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

    assert len(data["users"]) == 2
    assert user_info1["id"], user_info2["id"] in (
        data["users"][0]["id"],
        data["users"][1]["id"],
    )
    assert user_info1["username"], user_info2["username"] in (
        data["users"][0]["username"],
        data["users"][1]["username"],
    )
    assert user_info1["first_name"], user_info2["first_name"] in (
        data["users"][0]["first_name"],
        data["users"][1]["first_name"],
    )
    assert user_info1["last_name"], user_info2["last_name"] in (
        data["users"][0]["last_name"],
        data["users"][1]["last_name"],
    )
    assert user_info1["patronymic"], user_info2["patronymic"] in (
        data["users"][0]["patronymic"],
        data["users"][1]["patronymic"],
    )
    assert user_info1["employee_number"], user_info2["employee_number"] in (
        data["users"][0]["employee_number"],
        data["users"][1]["employee_number"],
    )

    role_from_database = await get_role_from_database(role_id)
    assert role_from_database["name"] == role_info["name"]
    assert role_from_database["permissions"] == role_info["permissions"]
    assert len(role_from_database["users"]) == 2
    assert user_info1["id"], user_info2["id"] in (
        role_from_database["users"][0]["id"],
        role_from_database["users"][1]["id"],
    )
    assert user_info1["username"], user_info2["username"] in (
        role_from_database["users"][0]["username"],
        role_from_database["users"][1]["username"],
    )
    assert user_info1["first_name"], user_info2["first_name"] in (
        role_from_database["users"][0]["first_name"],
        role_from_database["users"][1]["first_name"],
    )
    assert user_info1["last_name"], user_info2["last_name"] in (
        role_from_database["users"][0]["last_name"],
        role_from_database["users"][1]["last_name"],
    )
    assert user_info1["patronymic"], user_info2["patronymic"] in (
        role_from_database["users"][0]["patronymic"],
        role_from_database["users"][1]["patronymic"],
    )
    assert user_info1["employee_number"], user_info2["employee_number"] in (
        role_from_database["users"][0]["employee_number"],
        role_from_database["users"][1]["employee_number"],
    )


async def test_get_role_not_found(client, create_user_in_database):
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
