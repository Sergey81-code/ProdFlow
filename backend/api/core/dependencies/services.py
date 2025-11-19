from fastapi import Depends

from api.core.dependencies.repositories import (
    get_device_repository,
    get_role_repository,
    get_user_repository,
)
from api.v1.auth.service import AuthService
from api.v1.devices.repo_interface import IDeviceRepository
from api.v1.devices.service import DeviceService
from api.v1.roles.repo_interface import IRoleRepository
from api.v1.roles.service import RoleService
from api.v1.users.repo_interface import IUserRepository
from api.v1.users.service import UserService


async def get_role_service(
    repo: IRoleRepository = Depends(get_role_repository),
):
    return RoleService(repo)


async def get_user_service(
    repo: IUserRepository = Depends(get_user_repository),
    role_repo: IRoleRepository = Depends(get_role_repository),
):
    return UserService(repo, role_repo)


async def get_device_service(
    repo: IDeviceRepository = Depends(get_device_repository),
):
    return DeviceService(repo)


async def get_auth_service(
    repo: IDeviceRepository = Depends(get_user_repository),
):
    return AuthService(repo)
