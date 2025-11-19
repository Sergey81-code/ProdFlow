import pytest
from uuid import uuid4
from config.permissions import Permissions
from tests.conftest import ROLE_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_update_role_name_success(
    client, create_role_in_database, get_role_from_database
):
    role_id = uuid4()
    original = {
        "id": role_id,
        "name": "old name",
        "permissions": [Permissions.GET_DEVICES],
    }
    await create_role_in_database(original)

    body = {"name": "new name"}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])

    resp = client.patch(
        f"{VERSION_URL}{ROLE_URL}/{role_id}", json=body, headers=headers
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "new name"
    assert data["id"] == str(role_id)

    role_from_db = await get_role_from_database(role_id)
    assert role_from_db["name"] == "new name"


async def test_update_role_permissions_success(
    client, create_role_in_database, get_role_from_database
):
    role_id = uuid4()
    original = {
        "id": role_id,
        "name": "perm role",
        "permissions": [Permissions.GET_DEVICES],
    }
    await create_role_in_database(original)

    body = {"permissions": [Permissions.CREATE_DEVICE, Permissions.DELETE_DEVICE]}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])

    resp = client.patch(
        f"{VERSION_URL}{ROLE_URL}/{role_id}", json=body, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["permissions"] == body["permissions"]

    role_from_db = await get_role_from_database(role_id)
    assert set(role_from_db["permissions"]) == set(body["permissions"])


async def test_update_role_both_name_and_permissions(client, create_role_in_database):
    role_id = uuid4()
    await create_role_in_database(
        {
            "id": role_id,
            "name": "old",
            "permissions": [Permissions.GET_DEVICES],
        }
    )

    body = {"name": "updated", "permissions": [Permissions.CREATE_DEVICE]}

    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])
    resp = client.patch(
        f"{VERSION_URL}{ROLE_URL}/{role_id}", json=body, headers=headers
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == body["name"]
    assert data["permissions"] == body["permissions"]


@pytest.mark.parametrize(
    "existing, new", [("TestName", "testname"), ("RoleX", "ROLEX"), ("Admin", "aDmIn")]
)
async def test_update_role_duplicate_name_case_insensitive(
    client, create_role_in_database, existing, new
):
    first_id = uuid4()
    second_id = uuid4()

    await create_role_in_database(
        {
            "id": first_id,
            "name": existing,
            "permissions": [Permissions.GET_DEVICES],
        }
    )
    await create_role_in_database(
        {
            "id": second_id,
            "name": "other",
            "permissions": [Permissions.GET_DEVICES],
        }
    )

    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])
    resp = client.patch(
        f"{VERSION_URL}{ROLE_URL}/{second_id}", json={"name": new}, headers=headers
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": f"Role with name {new} already exists."}


async def test_update_role_not_found(client, create_role_in_database):
    role_id = uuid4()
    await create_role_in_database(
        {
            "id": role_id,
            "name": "old",
            "permissions": [Permissions.GET_DEVICES],
        }
    )
    rid = uuid4()
    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])
    resp = client.patch(
        f"{VERSION_URL}{ROLE_URL}/{rid}", json={"name": "x"}, headers=headers
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Role with this id not found"}


async def test_update_super_role_forbidden(
    client, create_role_in_database, get_project_settings
):
    settings = await get_project_settings()
    rid = uuid4()

    await create_role_in_database(
        {
            "id": rid,
            "name": settings.SUPER_ROLE_NAME,
            "permissions": [Permissions.GET_DEVICES],
        }
    )

    body = {"name": "new super name"}
    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])
    resp = client.patch(f"{VERSION_URL}{ROLE_URL}/{rid}", json=body, headers=headers)

    assert resp.status_code == 403
    assert resp.json() == {"detail": "Super role is not allowed to perform this action"}


async def test_update_role_unauth(
    client, create_role_in_database, get_project_settings
):
    rid = uuid4()
    await create_role_in_database({"id": rid, "name": "test", "permissions": []})

    resp = client.patch(f"{VERSION_URL}{ROLE_URL}/{rid}", json={"name": "x"})

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_update_role_no_permission(
    client, create_role_in_database, get_project_settings
):
    rid = uuid4()
    await create_role_in_database({"id": rid, "name": "test", "permissions": []})

    headers = await create_auth_headers_for_user([Permissions.GET_DEVICES])
    resp = client.patch(
        f"{VERSION_URL}{ROLE_URL}/{rid}", json={"name": "new"}, headers=headers
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


@pytest.mark.parametrize(
    "bad_id, expected_status_code",
    [("123", 422), ("not-uuid", 422), ("", 405), ("  ", 422)],
)
async def test_update_role_invalid_id(client, bad_id, expected_status_code):
    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])
    resp = client.patch(
        f"{VERSION_URL}{ROLE_URL}/{bad_id}", json={"name": "x"}, headers=headers
    )
    assert resp.status_code == expected_status_code


async def test_update_role_empty_body(client, create_role_in_database):
    rid = uuid4()
    await create_role_in_database({"id": rid, "name": "t", "permissions": []})

    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])
    resp = client.patch(f"{VERSION_URL}{ROLE_URL}/{rid}", json={}, headers=headers)

    assert resp.status_code == 422
    assert resp.json() == {"detail": "At least one parameter must be defined"}


async def test_update_role_invalid_permissions_type(client, create_role_in_database):
    rid = uuid4()
    await create_role_in_database({"id": rid, "name": "t", "permissions": []})

    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])
    resp = client.patch(
        f"{VERSION_URL}{ROLE_URL}/{rid}",
        json={"permissions": "not-a-list"},
        headers=headers,
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {
                "type": "list_type",
                "loc": ["body", "permissions"],
                "msg": "Input should be a valid list",
                "input": "not-a-list",
            }
        ]
    }


async def test_update_role_sql_injection_in_name(client, create_role_in_database):
    rid = uuid4()
    await create_role_in_database({"id": rid, "name": "inj", "permissions": []})

    headers = await create_auth_headers_for_user([Permissions.UPDATE_ROLE])

    malicious = "'; DROP TABLE roles; --"
    resp = client.patch(
        f"{VERSION_URL}{ROLE_URL}/{rid}", json={"name": malicious}, headers=headers
    )

    assert resp.status_code == 200
