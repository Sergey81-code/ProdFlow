from uuid import uuid4
import pytest
from config.permissions import Permissions
from tests.conftest import USER_URL, VERSION_URL
from tests.utils_for_tests import create_auth_headers_for_user


async def test_delete_user(
    client,
    create_role_in_database,
    create_user_in_database,
    get_user_from_database,
    create_department_in_database,
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": []}
    )

    department_id = uuid4()
    await create_department_in_database(
        {
            "id": department_id,
            "name": "test department name",
            "code": "some department code",
        }
    )

    user_data = {
        "id": uuid4(),
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "employee_number": "some_token123",
        "password": "StrongPass123!",
        "role_ids": [str(role_id)],
        "department_id": str(department_id),
    }

    user_id = await create_user_in_database(user_data)
    headers_for_auth = await create_auth_headers_for_user([Permissions.DELETE_USER])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=headers_for_auth,
    )

    assert resp.status_code == 200
    assert resp.json() == str(user_id)

    user_from_db = await get_user_from_database(user_id)
    assert user_from_db is None


async def test_delete_user_not_found(client, create_department_in_database):
    non_existing_id = uuid4()
    headers = await create_auth_headers_for_user([Permissions.DELETE_USER])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{non_existing_id}",
        headers=headers,
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "User with this id not found"}


@pytest.mark.parametrize(
    "bad_id",
    [
        "123",
        "not-a-uuid",
    ],
)
async def test_delete_user_invalid_id(client, bad_id):
    headers = await create_auth_headers_for_user([Permissions.DELETE_USER])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{bad_id}",
        headers=headers,
    )

    assert resp.status_code == 422

    data = resp.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    assert len(data["detail"]) == 1

    err = data["detail"][0]

    assert err["type"] == "uuid_parsing"
    assert err["loc"] == ["path", "user_id"]
    assert err["input"] == bad_id
    assert "UUID" in err["msg"]
    assert "error" in err["ctx"]


async def test_delete_user_unauth(
    client,
    create_role_in_database,
    create_user_in_database,
    get_project_settings,
    create_department_in_database,
):
    role_id = uuid4()
    await create_role_in_database({"id": role_id, "name": "x", "permissions": []})

    department_id = uuid4()
    await create_department_in_database(
        {
            "id": department_id,
            "name": "dep",
            "code": "d1",
        }
    )

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "bad",
            "first_name": "Bad",
            "last_name": "Token",
            "patronymic": "Test",
            "employee_number": "tok",
            "password": "123",
            "role_ids": [str(role_id)],
            "department_id": str(department_id),
        }
    )

    bad_headers = {"Authorization": "Bearer wrongtoken"}

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()

    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_delete_user_no_permissions(
    client,
    create_role_in_database,
    create_user_in_database,
    get_project_settings,
    create_department_in_database,
):
    role_id = uuid4()
    await create_role_in_database({"id": role_id, "name": "x", "permissions": []})

    department_id = uuid4()
    await create_department_in_database(
        {
            "id": department_id,
            "name": "dep",
            "code": "d1",
        }
    )

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "noperms",
            "first_name": "No",
            "last_name": "Perms",
            "patronymic": "Test",
            "employee_number": "tok",
            "password": "123",
            "role_ids": [str(role_id)],
            "department_id": str(department_id),
        }
    )

    headers = await create_auth_headers_for_user([Permissions.GET_USERS])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=headers,
    )

    settings = await get_project_settings()

    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 403
        assert resp.json() == {"detail": "Forbidden: insufficient permissions"}
    else:
        assert resp.status_code == 200


async def test_delete_user_bad_credentials(
    client,
    create_role_in_database,
    create_user_in_database,
    get_project_settings,
    create_department_in_database,
):
    role_id = uuid4()
    await create_role_in_database({"id": role_id, "name": "test", "permissions": []})

    department_id = uuid4()
    await create_department_in_database(
        {
            "id": department_id,
            "name": "dep",
            "code": "d1",
        }
    )

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "badcred",
            "first_name": "Bad",
            "last_name": "Cred",
            "patronymic": "Test",
            "employee_number": "tok",
            "password": "123",
            "role_ids": [str(role_id)],
            "department_id": str(department_id),
        }
    )

    bad_headers = {"Authorization": "Bearer 111"}

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=bad_headers,
    )

    settings = await get_project_settings()

    if settings.ENABLE_PERMISSION_CHECK:
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Could not validate credentials"}
    else:
        assert resp.status_code == 200


async def test_delete_super_user_not_allowed(
    client,
    create_role_in_database,
    create_user_in_database,
    get_project_settings,
    create_department_in_database,
):
    settings = await get_project_settings()

    role_id = uuid4()
    await create_role_in_database(
        {
            "id": role_id,
            "name": settings.SUPER_ROLE_NAME,
            "permissions": [p for p in Permissions],
        }
    )

    department_id = uuid4()
    await create_department_in_database(
        {
            "id": department_id,
            "name": "dep",
            "code": "d1",
        }
    )

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "superuser",
            "first_name": "Super",
            "last_name": "Admin",
            "patronymic": "Test",
            "employee_number": "tok",
            "password": "123",
            "role_ids": [str(role_id)],
            "department_id": str(department_id),
        }
    )

    headers = await create_auth_headers_for_user([Permissions.DELETE_USER])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=headers,
    )

    assert resp.status_code == 403
    assert resp.json() == {
        "detail": "User with super role is not allowed to perform this action"
    }


async def test_department_not_deleted_when_user_deleted(
    client,
    create_role_in_database,
    create_user_in_database,
    create_department_in_database,
    get_department_from_database,
):
    role_id = uuid4()
    await create_role_in_database(
        {"id": role_id, "name": "employee", "permissions": [Permissions.DELETE_USER]}
    )

    department_id = uuid4()
    await create_department_in_database(
        {
            "id": department_id,
            "name": "dep test",
            "code": "code123",
        }
    )

    user_id = await create_user_in_database(
        {
            "id": uuid4(),
            "username": "checkdep",
            "first_name": "John",
            "last_name": "Tester",
            "patronymic": "Q",
            "employee_number": "emp123",
            "password": "123",
            "role_ids": [str(role_id)],
            "department_id": str(department_id),
        }
    )

    headers = await create_auth_headers_for_user([Permissions.DELETE_USER])

    resp = client.delete(
        url=f"{VERSION_URL}{USER_URL}/{user_id}",
        headers=headers,
    )

    assert resp.status_code == 200

    dep = await get_department_from_database(department_id)
    assert dep is not None
    assert dep["id"] == department_id
