from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import DEPARTMENT_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_update_department_success(
    client, create_department_in_database, get_department_from_database
):
    department_id = uuid4()
    original = {
        "id": department_id,
        "name": "test department",
        "code": "a3f9c2b7d18e44fa",
    }
    await create_department_in_database(original)

    department_update_info = {"name": "new name", "code": "a3f9c2b7d18e44gb"}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{department_id}",
        json=department_update_info,
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == department_update_info["name"]
    assert data["code"] == department_update_info["code"]
    assert data["id"] == str(department_id)

    department_from_db = await get_department_from_database(department_id)
    assert department_from_db["name"] == department_update_info["name"]
    assert department_from_db["code"] == department_update_info["code"]


async def test_update_department_name_only(
    client, create_department_in_database, get_department_from_database
):
    dep_id = uuid4()
    original = {
        "id": dep_id,
        "name": "old name",
        "code": "old_code",
    }
    await create_department_in_database(original)

    body = {"name": "updated name"}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}", json=body, headers=headers
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "updated name"
    assert data["code"] == original["code"]

    dep = await get_department_from_database(dep_id)
    assert dep["name"] == "updated name"
    assert dep["code"] == original["code"]


async def test_update_department_code_only(
    client, create_department_in_database, get_department_from_database
):
    dep_id = uuid4()
    original = {
        "id": dep_id,
        "name": "department",
        "code": "code1",
    }
    await create_department_in_database(original)

    body = {"code": "code2"}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}", json=body, headers=headers
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "code2"
    assert data["name"] == original["name"]

    dep = await get_department_from_database(dep_id)
    assert dep["code"] == "code2"
    assert dep["name"] == original["name"]


@pytest.mark.parametrize(
    "existing, new",
    [("Department1", "department1"), ("MyDep", "MYDEP"), ("TestDep", "testdep")],
)
async def test_update_department_duplicate_name_case_insensitive(
    client, create_department_in_database, existing, new
):
    first_id = uuid4()
    second_id = uuid4()

    await create_department_in_database(
        {
            "id": first_id,
            "name": existing,
            "code": "codeA",
        }
    )

    await create_department_in_database(
        {
            "id": second_id,
            "name": "other department",
            "code": "codeB",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{second_id}",
        json={"name": new},
        headers=headers,
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": f"Department with provided parameters already exists"
    }


async def test_update_department_duplicate_code(client, create_department_in_database):
    first_id = uuid4()
    second_id = uuid4()

    await create_department_in_database(
        {
            "id": first_id,
            "name": "dep1",
            "code": "ABC123",
        }
    )

    await create_department_in_database(
        {
            "id": second_id,
            "name": "dep2",
            "code": "XYZ999",
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{second_id}",
        json={"code": "ABC123"},
        headers=headers,
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "Department with provided parameters already exists"
    }


async def test_update_department_not_found(client, create_department_in_database):
    dep_id = uuid4()
    await create_department_in_database(
        {
            "id": dep_id,
            "name": "existing dep",
            "code": "code123",
        }
    )

    non_existent = uuid4()
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{non_existent}",
        json={"name": "new name"},
        headers=headers,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "No departments found"}


async def test_update_department_unauth(
    client, create_department_in_database, get_project_settings
):
    dep_id = uuid4()
    await create_department_in_database(
        {
            "id": dep_id,
            "name": "test dep",
            "code": "code123",
        }
    )

    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}", json={"name": "new name"}
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_update_department_no_permission(
    client, create_department_in_database, get_project_settings
):
    dep_id = uuid4()
    await create_department_in_database(
        {"id": dep_id, "name": "dep", "code": "code123"}
    )

    headers = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}",
        json={"name": "new name"},
        headers=headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


async def test_update_department_bad_token(
    client, create_department_in_database, get_project_settings
):
    dep_id = uuid4()
    await create_department_in_database(
        {"id": dep_id, "name": "dep", "code": "code123"}
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    bad = {k: v + "broken" for k, v in headers.items()}
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}",
        json={"name": "new name"},
        headers=bad,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
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
async def test_update_department_invalid_id(client, bad_id, expected_status_code):
    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{bad_id}",
        json={"name": "new name"},
        headers=headers,
    )

    assert resp.status_code == expected_status_code


async def test_update_department_empty_body(client, create_department_in_database):
    dep_id = uuid4()
    await create_department_in_database(
        {"id": dep_id, "name": "test dep", "code": "code123"}
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}",
        json={},
        headers=headers,
    )

    assert resp.status_code == 422
    assert resp.json() == {"detail": "At least one parameter must be defined"}


async def test_update_department_invalid_name_type(
    client, create_department_in_database
):
    dep_id = uuid4()
    await create_department_in_database(
        {"id": dep_id, "name": "department", "code": "code"}
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}",
        json={"name": 123},
        headers=headers,
    )

    assert resp.status_code == 422


async def test_update_department_invalid_code_type(
    client, create_department_in_database
):
    dep_id = uuid4()
    await create_department_in_database(
        {"id": dep_id, "name": "department", "code": "code"}
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}",
        json={"code": 123},
        headers=headers,
    )

    assert resp.status_code == 422


async def test_update_department_name_too_long(client, create_department_in_database):
    dep_id = uuid4()
    await create_department_in_database({"id": dep_id, "name": "dep", "code": "code"})

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}",
        json={"name": "a" * 256},
        headers=headers,
    )

    assert resp.status_code == 422


async def test_update_department_code_too_long(client, create_department_in_database):
    dep_id = uuid4()
    await create_department_in_database({"id": dep_id, "name": "dep", "code": "code"})

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}",
        json={"code": "a" * 256},
        headers=headers,
    )

    assert resp.status_code == 422


async def test_update_department_sql_injection_in_name(
    client, create_department_in_database
):
    dep_id = uuid4()
    await create_department_in_database(
        {"id": dep_id, "name": "dep", "code": "code123"}
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    malicious = "'; DROP TABLE departments; --"
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}",
        json={"name": malicious},
        headers=headers,
    )

    assert resp.status_code == 200


async def test_update_department_sql_injection_in_code(
    client, create_department_in_database
):
    dep_id = uuid4()
    await create_department_in_database(
        {"id": dep_id, "name": "dep", "code": "code123"}
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_DEPARTMENT])
    malicious = "'; DROP TABLE departments; --"
    resp = client.patch(
        f"{VERSION_URL}{DEPARTMENT_URL}/{dep_id}",
        json={"code": malicious},
        headers=headers,
    )

    assert resp.status_code == 200
