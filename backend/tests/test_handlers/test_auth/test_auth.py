import datetime
import pytest
from uuid import uuid4
from jose import jwt

from config.permissions import Permissions
from tests.conftest import LOGIN_URL, VERSION_URL
from utils.hashing import Hasher


async def test_login_success(client, create_user_in_database, user_data):
    user_info = {
        "id": uuid4(),
        "username": user_data["username"],
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "finger_token": "some_token123",
        "password": Hasher.get_password_hash(user_data["password"]),
        "role_ids": [],
    }

    await create_user_in_database(user_info)

    response = client.post(
        url=f"{VERSION_URL}{LOGIN_URL}",
        data={"username": user_data["username"], "password": user_data["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 10


async def test_login_wrong_password(client, create_user_in_database, user_data):
    user_info = {
        "id": uuid4(),
        "username": user_data["username"],
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "finger_token": "some_token123",
        "password": Hasher.get_password_hash(user_data["password"]),
        "role_ids": [],
    }

    await create_user_in_database(user_info)

    response = client.post(
        url=f"{VERSION_URL}{LOGIN_URL}",
        data={"username": user_data["username"], "password": "Wrong!!!"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


async def test_login_user_not_found(client, create_user_in_database, user_data):
    user_info = {
        "id": uuid4(),
        "username": user_data["username"],
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "finger_token": "some_token123",
        "password": Hasher.get_password_hash(user_data["password"]),
        "role_ids": [],
    }

    await create_user_in_database(user_info)
    response = client.post(
        url=f"{VERSION_URL}{LOGIN_URL}",
        data={"username": "nobody", "password": user_data["password"]},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


@pytest.mark.parametrize(
    "data",
    [
        {"password": "x"},
        {"username": "john"},
        {},
    ],
)
async def test_login_missing_fields(client, data):
    response = client.post(url=f"{VERSION_URL}{LOGIN_URL}", data=data)
    assert response.status_code == 422


async def test_login_wrong_content_type_json(client):
    response = client.post(
        url=f"{VERSION_URL}{LOGIN_URL}", json={"username": "john", "password": "123"}
    )
    assert response.status_code == 422


async def test_login_response_shape(
    client,
    create_role_in_database,
    create_user_in_database,
    user_data,
    get_project_settings,
):

    role_info1 = {
        "id": uuid4(),
        "name": "employee",
        "permissions": [
            Permissions.CREATE_DEVICE,
            Permissions.CREATE_ROLE,
            Permissions.GET_USERS,
        ],
    }
    role_info2 = {
        "id": uuid4(),
        "name": "employer",
        "permissions": [
            Permissions.CREATE_USER,
            Permissions.DELETE_USER,
            Permissions.GET_USERS,
            Permissions.UPDATE_USER,
        ],
    }

    await create_role_in_database(role_info1)
    await create_role_in_database(role_info2)

    user_info = {
        "id": uuid4(),
        "username": user_data["username"],
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Martin",
        "finger_token": "some_token123",
        "password": Hasher.get_password_hash(user_data["password"]),
        "role_ids": [str(role_info1["id"]), str(role_info2["id"])],
    }

    await create_user_in_database(user_info)

    response = client.post(
        url=f"{VERSION_URL}{LOGIN_URL}",
        data={"username": user_data["username"], "password": user_data["password"]},
    )

    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {"access_token", "token_type"}
    assert data["token_type"] == "bearer"

    token = data["access_token"]

    settings = await get_project_settings()

    decoded = jwt.decode(
        token,
        settings.SECRET_KEY_FOR_ACCESS,
        algorithms=[settings.ALGORITHM],
    )

    assert "sub" in decoded
    assert "exp" in decoded
    assert "user_id" in decoded
    assert "roles" in decoded
    assert "permissions" in decoded

    assert decoded["sub"] == user_info["username"]

    assert decoded["user_id"] == str(user_info["id"])

    assert decoded["roles"] == user_info["role_ids"]

    expected_permissions = set(role_info1["permissions"] + role_info2["permissions"])
    assert len(decoded["permissions"]) == len(expected_permissions)
    assert set(decoded["permissions"]) == expected_permissions

    exp_timestamp = decoded["exp"]
    exp_dt = datetime.datetime.fromtimestamp(exp_timestamp, datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)

    delta = exp_dt - now
    assert delta.total_seconds() > 0
    assert delta.total_seconds() <= settings.TOKEN_EXPIRE_MINUTES * 60 + 20
