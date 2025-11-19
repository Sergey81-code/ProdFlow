import pytest
from uuid import uuid4
from config.permissions import Permissions
from tests.conftest import USER_URL, VERSION_URL
from tests.utils_for_tests import (
    create_auth_headers_for_user,
    _create_users,
    _create_roles,
)


async def test_get_user(client, create_user_in_database, create_role_in_database):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    user_id = uuid4()
    user_info = {
        "id": user_id,
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "finger_token": "some_token123",
        "role_ids": role_ids,
    }

    await create_user_in_database(user_info)
    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(f"{VERSION_URL}{USER_URL}/{str(user_id)}", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(user_id)
    assert data["username"] == user_info["username"]
    assert data["first_name"] == user_info["first_name"]
    assert data["last_name"] == user_info["last_name"]
    assert data["patronymic"] == user_info["patronymic"]
    assert data["finger_token"] == user_info["finger_token"]
    assert data["role_ids"] == user_info["role_ids"]


async def test_get_user_not_found(client):
    non_existing_id = uuid4()
    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(
        f"{VERSION_URL}{USER_URL}/{str(non_existing_id)}", headers=headers
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "User with this id not found"}


@pytest.mark.parametrize(
    "bad_id",
    ["123", "not-uuid", "0000"],
)
async def test_get_user_invalid_uuid(client, bad_id):
    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(f"{VERSION_URL}{USER_URL}/{bad_id}", headers=headers)

    assert resp.status_code == 422


async def test_get_user_unauthorized(
    client, create_user_in_database, get_project_settings
):
    user_id = uuid4()
    await create_user_in_database(
        {"id": user_id, "username": "john", "first_name": "John", "last_name": "Doe"}
    )

    resp = client.get(f"{VERSION_URL}{USER_URL}/{user_id}")

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_get_user_bad_token(
    client, create_user_in_database, get_project_settings
):

    user_id = uuid4()
    await create_user_in_database(
        {"id": user_id, "username": "john", "first_name": "John", "last_name": "Doe"}
    )

    headers = await create_auth_headers_for_user([Permissions.CREATE_USER])
    bad = {k: v + "broken" for k, v in headers.items()}

    resp = client.get(f"{VERSION_URL}{USER_URL}/{user_id}", headers=bad)

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_get_user_forbidden_no_permissions(
    client, create_user_in_database, get_project_settings
):
    user_id = uuid4()
    await create_user_in_database(
        {"id": user_id, "username": "john", "first_name": "John", "last_name": "Doe"}
    )

    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(f"{VERSION_URL}{USER_URL}/{user_id}", headers=headers)

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


async def test_get_all_users(client, create_role_in_database, create_user_in_database):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    users = await _create_users(create_user_in_database, role_ids)

    headers = await create_auth_headers_for_user([Permissions.GET_USERS])
    resp = client.get(f"{VERSION_URL}{USER_URL}/", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == len(users)


async def test_get_users_by_name_exact_match(
    client, create_role_in_database, create_user_in_database
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)

    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(f"{VERSION_URL}{USER_URL}/?name=johndoe1", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["username"] == "johndoe1"


async def test_get_users_by_name_case_insensitive(
    client, create_role_in_database, create_user_in_database
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)
    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(f"{VERSION_URL}{USER_URL}/?name=JoHnDoE1", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1


async def test_get_users_by_name_partial_match(
    client, create_role_in_database, create_user_in_database
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)
    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(f"{VERSION_URL}{USER_URL}/?name=do", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


async def test_get_users_by_name_no_results(
    client, create_role_in_database, create_user_in_database
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)
    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(f"{VERSION_URL}{USER_URL}/?name=unknown", headers=headers)

    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_users_unauthorized_no_token(
    client, create_role_in_database, create_user_in_database, get_project_settings
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)
    resp = client.get(f"{VERSION_URL}{USER_URL}/")

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_get_users_bad_token(
    client, create_role_in_database, create_user_in_database, get_project_settings
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)

    headers = await create_auth_headers_for_user([Permissions.GET_USERS])
    bad = {k: v + "broken" for k, v in headers.items()}

    resp = client.get(f"{VERSION_URL}{USER_URL}/", headers=bad)

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_get_users_forbidden(
    client, create_role_in_database, create_user_in_database, get_project_settings
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)
    headers = await create_auth_headers_for_user([Permissions.GET_ROLES])

    resp = client.get(f"{VERSION_URL}{USER_URL}/", headers=headers)

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


async def test_get_users_by_first_name(
    client, create_role_in_database, create_user_in_database
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)
    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(f"{VERSION_URL}{USER_URL}/?name=first", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all("first" in u["first_name"].lower() for u in data)


async def test_get_users_by_last_name(
    client, create_role_in_database, create_user_in_database
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)
    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(f"{VERSION_URL}{USER_URL}/?name=last", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all("last" in u["last_name"].lower() for u in data)


async def test_get_users_by_patronymic(
    client, create_role_in_database, create_user_in_database
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    await _create_users(create_user_in_database, role_ids)
    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.get(f"{VERSION_URL}{USER_URL}/?name=Martin", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all("Martin" in u["patronymic"] for u in data)


@pytest.mark.parametrize(
    "query, expected",
    [
        ("first", [0, 1, 2]),
        ("FIRST", [0, 1, 2]),
        ("First", [0, 1, 2]),
        ("last1", [0]),
        ("last2", [1]),
        ("last3", [2]),
        ("martin1", [0]),
        ("martin2", [1]),
        ("martin3", [2]),
        ("martin", [0, 1, 2]),
        ("las", [0, 1, 2]),
        ("stin", []),
        ("first last1", [0]),
        ("last1 first", [0]),
        ("first last2", [1]),
        ("last3 first martin3", [2]),
        ("first last4", []),
        ("unknown", []),
        ("FIRST LAST2", [1]),
        ("mArTiN3", [2]),
        ("martin1@", [0]),
        ("martin(2)", [1]),
        ("martin-3", [2]),
        ("first first last2", [1]),
        ("last3 last3 last3", [2]),
        ("   first   last2   ", [1]),
        ("", [0, 1, 2]),
        ("first mart", [0, 1, 2]),
        ("las mar first", [0, 1, 2]),
        ("иван", []),
        ("firs", [0, 1, 2]),
    ],
)
async def test_fulltext_search_parametrized(
    client,
    create_role_in_database,
    create_user_in_database,
    query,
    expected,
):
    role_ids = [
        str(role["id"]) for role in await _create_roles(create_role_in_database)
    ]
    users = await _create_users(create_user_in_database, role_ids)

    headers = await create_auth_headers_for_user([Permissions.GET_USERS])
    resp = client.get(f"{VERSION_URL}{USER_URL}/?name={query}", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    expected_ids = {str(users[i]["id"]) for i in expected}
    returned_ids = {u["id"] for u in data}

    assert returned_ids == expected_ids, (
        f"\nQuery: {query!r}\n"
        f"Expected count: {len(expected_ids)} -> {expected_ids}\n"
        f"Got: {len(returned_ids)} -> {returned_ids}\n"
        f"Returned data: {data}"
    )
