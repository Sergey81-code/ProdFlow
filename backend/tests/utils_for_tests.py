import datetime
from uuid import uuid4
from jose import jwt

from api.core.config import get_settings
from config.permissions import Permissions


settings = get_settings()


async def create_jwt_token(permissions: list[str]) -> str:
    token_key = settings.SECRET_KEY_FOR_ACCESS
    token_time = 30
    to_encode = {"permissions": permissions}
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=token_time
    )
    to_encode.update({"sub": "test@mail.ru"})
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, token_key, algorithm=settings.ALGORITHM)


async def create_auth_headers_for_user(permissions: list[str]) -> dict[str]:
    token = await create_jwt_token(permissions)
    return {"Authorization": f"Bearer {token}"}


async def _create_roles(create_role_in_database):
    roles = [
        {
            "id": uuid4(),
            "name": "Admin",
            "permissions": [Permissions.CREATE_DEVICE],
        },
        {
            "id": uuid4(),
            "name": "Viewer",
            "permissions": [Permissions.GET_DEVICES],
        },
        {
            "id": uuid4(),
            "name": "SuperUser",
            "permissions": [Permissions.CREATE_DEVICE, Permissions.DELETE_DEVICE],
        },
    ]
    for role in roles:
        await create_role_in_database(role)
    return roles


async def _create_devices(create_device_in_database):
    devices = [
        {
            "id": uuid4(),
            "name": "Test Device 1",
            "android_id": "a3f9c2b7d18e44fa",
        },
        {
            "id": uuid4(),
            "name": "Test Device 2",
            "android_id": "a4f9c2b7d18e44fa",
        },
        {
            "id": uuid4(),
            "name": "Test Device 3",
            "android_id": "a5f9c2b7d18e44fa",
        },
    ]
    for device in devices:
        await create_device_in_database(device)
    return devices


async def _create_users(create_user_in_database, role_ids):
    users = [
        {
            "id": uuid4(),
            "username": "johndoe1",
            "first_name": "FIRST1",
            "last_name": "LAST1",
            "patronymic": "Martin1",
            "finger_token": "some_token1231",
            "password": "StrongPass123!1",
            "role_ids": role_ids,
        },
        {
            "id": uuid4(),
            "username": "johndoe2",
            "first_name": "FIRST1",
            "last_name": "LAST2",
            "patronymic": "Martin2",
            "finger_token": "some_token1232",
            "password": "StrongPass1232!",
            "role_ids": role_ids,
        },
        {
            "id": uuid4(),
            "username": "johndoe3",
            "first_name": "FIRST1",
            "last_name": "LAST3",
            "patronymic": "Martin3",
            "finger_token": "some_token1233",
            "password": "StrongPass123!3",
            "role_ids": role_ids,
        },
    ]
    for user in users:
        await create_user_in_database(user)
    return users
