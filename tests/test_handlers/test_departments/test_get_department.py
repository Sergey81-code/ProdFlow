from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import DEPARTMENT_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user, _create_departments


async def test_get_department(
    client, create_department_in_database, get_department_from_database
):
    department_id = uuid4()
    department_info = {
        "name": "test department name",
        "code": "some department code",
    }

    await create_department_in_database({"id": department_id, **department_info})
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(f"{VERSION_URL}{DEPARTMENT_URL}/{department_id}", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(department_id)
    assert data["name"] == department_info["name"]
    assert data["code"] == department_info["code"]

    department_from_db = await get_department_from_database(department_id)
    assert department_from_db["name"] == department_info["name"]
    assert department_from_db["code"] == department_info["code"]


async def test_get_department_not_found(client):
    non_existing_id = uuid4()
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/{non_existing_id}", headers=headers
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "No departments found"}


async def test_get_department_unauth(
    client, create_department_in_database, get_project_settings
):
    department_id = uuid4()
    department_info = {"name": "test", "code": "abc123"}
    await create_department_in_database({"id": department_id, **department_info})

    bad_headers = {"Authorization": "Bearer wrongtoken"}

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/{department_id}", headers=bad_headers
    )
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_get_department_no_permissions(
    client, create_department_in_database, get_project_settings
):
    department_id = uuid4()
    department_info = {"name": "test", "code": "abc123"}
    await create_department_in_database({"id": department_id, **department_info})

    headers = await create_auth_headers_for_user([Permissions.CREATE_DEPARTMENT])

    resp = client.get(f"{VERSION_URL}{DEPARTMENT_URL}/{department_id}", headers=headers)

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
                        "loc": ["path", "department_id"],
                        "msg": (
                            "Input should be a valid UUID, invalid length: expected length 32 "
                            "for simple format, found 3"
                        ),
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
                        "loc": ["path", "department_id"],
                        "msg": (
                            "Input should be a valid UUID, invalid character: expected an optional "
                            "prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `n` at 1"
                        ),
                        "input": "not-a-uuid",
                        "ctx": {
                            "error": (
                                "invalid character: expected an optional prefix of `urn:uuid:` "
                                "followed by [0-9a-fA-F-], found `n` at 1"
                            )
                        },
                    }
                ]
            },
        ),
    ],
)
async def test_get_department_invalid_id(
    client, create_department_in_database, bad_id, expected_status_code, expected_detail
):
    department_id = uuid4()
    department_info = {"name": "test", "code": "abc123"}
    await create_department_in_database({"id": department_id, **department_info})

    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(f"{VERSION_URL}{DEPARTMENT_URL}/{bad_id}", headers=headers)
    assert resp.status_code == expected_status_code
    assert resp.json() == expected_detail


async def test_get_all_departments(client, create_department_in_database):
    departments = await _create_departments(create_department_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(f"{VERSION_URL}{DEPARTMENT_URL}/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data, list)
    assert len(data) == len(departments)


async def test_get_departments_by_name_exact(client, create_department_in_database):
    await _create_departments(create_department_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/?department_name=Test Department 1",
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Department 1"


async def test_get_departments_by_name_case_insensitive(
    client, create_department_in_database
):
    await _create_departments(create_department_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/?department_name=tEsT DePaRtMeNt 1",
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Department 1"


async def test_get_departments_by_name_partial(client, create_department_in_database):
    departments = await _create_departments(create_department_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/?department_name=Dep",
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == len(departments)


async def test_get_departments_no_results(client, create_department_in_database):
    await _create_departments(create_department_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/?department_name=unknown",
        headers=headers,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "No departments found"}


async def test_get_departments_empty_query_returns_all(
    client, create_department_in_database
):
    departments = await _create_departments(create_department_in_database)
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/?department_name=",
        headers=headers,
    )

    assert resp.status_code == 200
    assert len(resp.json()) == len(departments)


async def test_get_departments_unauthorized_no_token(
    client, create_department_in_database, get_project_settings
):
    await _create_departments(create_department_in_database)

    resp = client.get(f"{VERSION_URL}{DEPARTMENT_URL}/")
    settings = await get_project_settings()

    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_get_departments_forbidden(
    client, create_department_in_database, get_project_settings
):
    await _create_departments(create_department_in_database)
    headers = await create_auth_headers_for_user([Permissions.CREATE_DEPARTMENT])

    resp = client.get(f"{VERSION_URL}{DEPARTMENT_URL}/", headers=headers)
    settings = await get_project_settings()

    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


async def test_get_departments_wrong_token(
    client, create_department_in_database, get_project_settings
):
    await _create_departments(create_department_in_database)

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/",
        headers={"Authorization": "Bearer invalid"},
    )

    settings = await get_project_settings()

    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_get_department_by_code(
    client, create_department_in_database, get_department_from_database
):
    department_id = uuid4()
    code = "abc123"
    department_info = {"name": "test department", "code": code}

    await create_department_in_database({"id": department_id, **department_info})
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/code/{code}",
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["id"] == str(department_id)
    assert data["name"] == department_info["name"]
    assert data["code"] == code

    department_from_db = await get_department_from_database(department_id)
    assert department_from_db["code"] == code


async def test_get_department_by_code_not_found(client):
    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])
    code = "missing_code"

    resp = client.get(
        f"{VERSION_URL}{DEPARTMENT_URL}/code/{code}",
        headers=headers,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No departments found"}


async def test_get_department_by_code_unauthorized(
    client, create_department_in_database, get_project_settings
):
    department_id = uuid4()
    code = "abc123"

    await create_department_in_database(
        {"id": department_id, "name": "test dep", "code": code}
    )

    resp = client.get(f"{VERSION_URL}{DEPARTMENT_URL}/code/{code}")

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


@pytest.mark.parametrize(
    "bad_code, expected_status_code, expected_detail",
    [
        (
            "",
            422,
            {
                "detail": [
                    {
                        "type": "uuid_parsing",
                        "loc": ["path", "department_id"],
                        "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `o` at 2",
                        "input": "code",
                        "ctx": {
                            "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `o` at 2"
                        },
                    }
                ]
            },
        ),
        (None, 404, {"detail": "No departments found"}),
    ],
)
async def test_get_department_by_code_invalid(
    client,
    create_department_in_database,
    bad_code,
    expected_status_code,
    expected_detail,
):
    department_id = uuid4()

    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    await create_department_in_database(
        {"id": department_id, "name": "dep", "code": "valid_code"}
    )

    resp = client.get(f"{VERSION_URL}{DEPARTMENT_URL}/code/{bad_code}", headers=headers)

    assert resp.status_code == expected_status_code
    assert resp.json() == expected_detail
