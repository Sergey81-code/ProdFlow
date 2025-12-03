from typing import Any
from uuid import uuid4
import pytest
from config.permissions import Permissions
from tests.conftest import DEPARTMENT_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_create_department(client, get_department_from_database):
    department_info = {
        "name": "test department name",
        "code": "some department code",
    }
    resp = client.post(
        f"{VERSION_URL}{DEPARTMENT_URL}/",
        json=department_info,
        headers=await create_auth_headers_for_user([Permissions.CREATE_DEPARTMENT]),
    )
    assert resp.status_code == 200
    data_from_resp = resp.json()
    assert data_from_resp["name"] == department_info["name"]
    assert data_from_resp["code"] == department_info["code"]

    department_from_db: dict[str, Any] = await get_department_from_database(
        data_from_resp["id"]
    )
    assert department_from_db["name"] == department_info["name"]
    assert department_from_db["code"] == department_info["code"]


@pytest.mark.parametrize(
    "existing_name,new_name",
    [
        ("Test Department", "Test Department"),
        ("Test Department", "test department"),
        ("TeSt DePaRtMeNt", "TEST DEPARTMENT"),
        ("Another Name", "another name"),
    ],
)
async def test_create_department_duplicate_name_case_insensitive(
    client, create_department_in_database, existing_name, new_name
):
    await create_department_in_database(
        {"id": uuid4(), "name": existing_name, "code": "unique_code1"}
    )

    resp = client.post(
        f"{VERSION_URL}{DEPARTMENT_URL}/",
        json={"name": new_name, "code": "unique_code2"},
        headers=await create_auth_headers_for_user([Permissions.CREATE_DEPARTMENT]),
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "Department with provided parameters already exists"
    }


@pytest.mark.parametrize(
    "existing_code,new_code",
    [
        ("CODE123", "CODE123"),
        ("code123", "code123"),
    ],
)
async def test_create_department_duplicate_code_case_insensitive(
    client, create_department_in_database, existing_code, new_code
):
    await create_department_in_database(
        {"id": uuid4(), "name": "Some Department", "code": existing_code}
    )

    resp = client.post(
        f"{VERSION_URL}{DEPARTMENT_URL}/",
        json={"name": "New Department", "code": new_code},
        headers=await create_auth_headers_for_user([Permissions.CREATE_DEPARTMENT]),
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "Department with provided parameters already exists"
    }


async def test_create_department_not_authenticated(client, get_project_settings):
    resp = client.post(
        f"{VERSION_URL}{DEPARTMENT_URL}/",
        json={"name": "Test", "code": "some_code"},
    )
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_create_department_bad_token(client, get_project_settings):
    headers = await create_auth_headers_for_user([Permissions.CREATE_DEPARTMENT])
    bad_headers = {k: v + "broken" for k, v in headers.items()}
    resp = client.post(
        f"{VERSION_URL}{DEPARTMENT_URL}/",
        json={"name": "Test", "code": "some_code"},
        headers=bad_headers,
    )
    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_create_department_no_permission(client, get_project_settings):
    resp = client.post(
        f"{VERSION_URL}{DEPARTMENT_URL}/",
        json={"name": "Test", "code": "some_code"},
        headers=await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS]),
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
        ({}, ["name", "code"]),
        ({"name": "Test"}, ["code"]),
        ({"code": "some_code"}, ["name"]),
        ({"name": None, "code": "some_code"}, ["name"]),
        ({"name": "Test Department1", "code": None}, ["code"]),
        ({"name": "", "code": "some_code"}, ["name"]),
        ({"name": "Test Department2", "code": ""}, ["code"]),
        ({"name": 123, "code": "some_code"}, ["name"]),
        ({"name": "Test Department3", "code": 12345}, ["code"]),
        ({"name": "", "code": None}, ["code"]),
    ],
)
async def test_create_department_validation(client, body, expected_missing):
    resp = client.post(
        f"{VERSION_URL}{DEPARTMENT_URL}/",
        json=body,
        headers=await create_auth_headers_for_user([Permissions.CREATE_DEPARTMENT]),
    )
    assert resp.status_code == 422
    error_text = str(resp.json())
    for field in expected_missing:
        assert field in error_text, f"Field '{field}' not found in error: {error_text}"
