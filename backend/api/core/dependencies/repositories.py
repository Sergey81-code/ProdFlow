from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.postgres.devicesRepo import PostgresDeviceRepo
from db.repositories.postgres.roleRepo import PostgresRoleRepo
from db.repositories.postgres.usersRepo import PostgresUserRepo
from db.session import get_session


async def get_role_repository(session: AsyncSession = Depends(get_session)):
    return PostgresRoleRepo(session)


async def get_user_repository(session: AsyncSession = Depends(get_session)):
    return PostgresUserRepo(session)


async def get_device_repository(session: AsyncSession = Depends(get_session)):
    return PostgresDeviceRepo(session)
