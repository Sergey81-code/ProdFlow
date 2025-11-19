from typing import Any
from uuid import uuid4

import pytest

from config.permissions import Permissions
from tests.conftest import ROLE_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_create_role(client, get_role_from_database):
    role_info = {
        "name": "test role",
        "permissions": [
            Permissions.CREATE_DEVICE,
            Permissions.DELETE_DEVICE,
            Permissions.GET_DEVICES,
            Permissions.UPDATE_DEVICE,
        ],
    }

    resp = client.post(
        f"{VERSION_URL}{ROLE_URL}/",
        json=role_info,
        headers=await create_auth_headers_for_user([Permissions.CREATE_ROLE]),
    )

    assert resp.status_code == 200
    data_from_resp = resp.json()

    assert data_from_resp["name"] == role_info["name"]
    assert data_from_resp["permissions"] == role_info["permissions"]

    role_from_db: dict[str, Any] = await get_role_from_database(data_from_resp["id"])

    assert role_from_db["name"] == role_info["name"]
    assert role_from_db["permissions"] == role_info["permissions"]


@pytest.mark.parametrize(
    "existing_name, new_name",
    [
        ("Test Duplicate", "test duplicate"),
        ("Test Duplicate", "TEST DUPLICATE"),
        ("Test Duplicate", "TeSt DuPlIcAtE"),
    ],
)
async def test_create_role_duplicate_name_case_insensitive(
    client, create_role_in_database, existing_name, new_name
):
    await create_role_in_database(
        {
            "id": uuid4(),
            "name": existing_name,
            "permissions": [Permissions.CREATE_DEVICE],
        }
    )

    resp = client.post(
        f"{VERSION_URL}{ROLE_URL}/",
        json={"name": new_name, "permissions": [Permissions.CREATE_DEVICE]},
        headers=await create_auth_headers_for_user([Permissions.CREATE_ROLE]),
    )

    assert resp.status_code == 400
    assert resp.json() == {"detail": f"Role with name {new_name} already exists."}


async def test_create_role_not_authenticated(client, get_project_settings):
    role_info = {
        "name": "Test Role",
        "permissions": [Permissions.CREATE_DEVICE],
    }

    resp = client.post(f"{VERSION_URL}{ROLE_URL}/", json=role_info)

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Not authenticated"}
    else:
        assert resp.status_code == 200


async def test_create_role_bad_token(client, get_project_settings):
    role_info = {
        "name": "Bad Token Role",
        "permissions": [Permissions.CREATE_DEVICE],
    }

    headers = await create_auth_headers_for_user([Permissions.CREATE_ROLE])
    bad_headers = {next(iter(headers)): next(iter(headers.values())) + "a"}

    resp = client.post(f"{VERSION_URL}{ROLE_URL}/", json=role_info, headers=bad_headers)

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_create_role_no_privilege(client, get_project_settings):
    role_info = {
        "name": "No Privilege Role",
        "permissions": [Permissions.CREATE_DEVICE],
    }

    resp = client.post(
        f"{VERSION_URL}{ROLE_URL}/",
        json=role_info,
        headers=await create_auth_headers_for_user([Permissions.GET_DEVICES]),
    )

    settings = await get_project_settings()
    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


@pytest.mark.parametrize(
    "role_info, expected_status, expected_detail_contains",
    [
        ({}, 422, "Field required"),
        ({"permissions": [Permissions.CREATE_DEVICE]}, 422, "name"),
        (
            {"name": None, "permissions": [Permissions.CREATE_DEVICE]},
            422,
            "Input should be a valid string",
        ),
        (
            {"name": "", "permissions": [Permissions.CREATE_DEVICE]},
            422,
            "String should have at least 1 character",
        ),
    ],
)
async def test_create_role_validation(
    client, role_info, expected_status, expected_detail_contains
):
    resp = client.post(
        f"{VERSION_URL}{ROLE_URL}/",
        json=role_info,
        headers=await create_auth_headers_for_user([Permissions.CREATE_ROLE]),
    )

    assert resp.status_code == expected_status
    assert expected_detail_contains in str(resp.json())


async def test_create_role_super_admin_not_allowed(client, get_project_settings):

    settings = await get_project_settings()
    role_info = {
        "name": settings.SUPER_ROLE_NAME,
        "permissions": [
            Permissions.CREATE_DEVICE,
            Permissions.DELETE_DEVICE,
            Permissions.GET_DEVICES,
            Permissions.UPDATE_DEVICE,
        ],
    }

    resp = client.post(
        f"{VERSION_URL}{ROLE_URL}/",
        json=role_info,
        headers=await create_auth_headers_for_user([Permissions.CREATE_ROLE]),
    )

    assert resp.status_code == 403
    assert resp.json() == {"detail": "Role with this name is not allowed to create"}


async def test_create_role_super_admin_not_allowed_uppercase(
    client, get_project_settings
):
    settings = await get_project_settings()
    role_info = {
        "name": settings.SUPER_ROLE_NAME.upper(),
        "permissions": [Permissions.CREATE_DEVICE],
    }

    resp = client.post(
        f"{VERSION_URL}{ROLE_URL}/",
        json=role_info,
        headers=await create_auth_headers_for_user([Permissions.CREATE_ROLE]),
    )

    assert resp.status_code == 403
    assert resp.json() == {"detail": "Role with this name is not allowed to create"}
