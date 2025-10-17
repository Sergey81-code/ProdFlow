from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.postgres.devicesRepo import DeviceRepository
from db.repositories.postgres.roleRepo import RoleRepository
from db.repositories.postgres.usersRepo import UserRepository
from db.session import get_session


async def get_role_repository(session: AsyncSession = Depends(get_session)):
    return RoleRepository(session)


async def get_user_repository(session: AsyncSession = Depends(get_session)):
    return UserRepository(session)


async def get_device_repository(session: AsyncSession = Depends(get_session)):
    return DeviceRepository(session)
