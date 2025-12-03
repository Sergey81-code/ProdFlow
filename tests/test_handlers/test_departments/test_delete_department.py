from typing import Any
from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import DEPARTMENT_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_delete_department(
    client, create_department_in_database, get_department_from_database
):
    department_id = uuid4()
    department_info = {
        "id": department_id,
        "name": "test department name",
        "code": "some department code",
    }

    await create_department_in_database(department_info)
    headers_for_auth = await create_auth_headers_for_user(
        [Permissions.DELETE_DEPARTMENT]
    )

    resp = client.delete(
        url=f"{VERSION_URL}{DEPARTMENT_URL}/{department_id}",
        headers=headers_for_auth,
    )
    assert resp.status_code == 200
    assert resp.json() == str(department_id)

    department_from_db: dict[str, Any] | None = await get_department_from_database(
        department_id
    )
    assert department_from_db is None


async def test_delete_department_not_found(client):
    non_existing_id = uuid4()
    headers_for_auth = await create_auth_headers_for_user(
        [Permissions.DELETE_DEPARTMENT]
    )

    resp = client.delete(
        url=f"{VERSION_URL}{DEPARTMENT_URL}/{non_existing_id}",
        headers=headers_for_auth,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Department with this id not found"}


async def test_delete_department_unauth(
    client, create_department_in_database, get_project_settings
):
    department_id = uuid4()
    await create_department_in_database(
        {"id": department_id, "name": "Unauth Dep", "code": "code123"}
    )

    bad_headers = {"Authorization": "Bearer wrongtoken"}

    resp = client.delete(
        url=f"{VERSION_URL}{DEPARTMENT_URL}/{department_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_delete_department_no_permissions(
    client, create_department_in_database, get_project_settings
):
    department_id = uuid4()
    await create_department_in_database(
        {"id": department_id, "name": "No Perm Dep", "code": "code999"}
    )

    headers_for_auth = await create_auth_headers_for_user([Permissions.GET_DEPARTMENTS])

    resp = client.delete(
        url=f"{VERSION_URL}{DEPARTMENT_URL}/{department_id}",
        headers=headers_for_auth,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


@pytest.mark.parametrize(
    "bad_id",
    ["123", "not-a-uuid", "xxxxx-zzzz", " "],
)
async def test_delete_department_invalid_id(client, bad_id):
    headers_for_auth = await create_auth_headers_for_user(
        [Permissions.DELETE_DEPARTMENT]
    )

    resp = client.delete(
        url=f"{VERSION_URL}{DEPARTMENT_URL}/{bad_id}",
        headers=headers_for_auth,
    )

    assert resp.status_code == 422

    data = resp.json()

    assert "detail" in data
    assert isinstance(data["detail"], list)
    err = data["detail"][0]

    assert err["type"] == "uuid_parsing"
    assert err["loc"] == ["path", "department_id"]
    assert bad_id in err.get("input", "")
    assert "UUID" in err.get("msg", "")


async def test_delete_department_method_not_allowed(client):
    headers_for_auth = await create_auth_headers_for_user(
        [Permissions.DELETE_DEPARTMENT]
    )

    resp = client.delete(
        url=f"{VERSION_URL}{DEPARTMENT_URL}/{""}",
        headers=headers_for_auth,
    )

    assert resp.status_code == 405

    assert resp.json() == {"detail": "Method Not Allowed"}


async def test_delete_department_bad_credentials(
    client, create_department_in_database, get_project_settings
):
    department_id = uuid4()
    await create_department_in_database(
        {"id": department_id, "name": "Bad Cred Dep", "code": "code777"}
    )

    bad_headers = {"Authorization": "Bearer 111"}

    resp = client.delete(
        url=f"{VERSION_URL}{DEPARTMENT_URL}/{department_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200
