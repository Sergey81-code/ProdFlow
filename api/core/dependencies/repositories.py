from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.postgres.deviceRepo import PostgresDeviceRepo
from db.repositories.postgres.roleRepo import PostgresRoleRepo
from db.repositories.postgres.userRepo import PostgresUserRepo
from db.repositories.postgres.departmentRepo import PostgresDepartmentRepo
from db.session import get_session


async def get_role_repository(session: AsyncSession = Depends(get_session)):
    return PostgresRoleRepo(session)


async def get_user_repository(session: AsyncSession = Depends(get_session)):
    return PostgresUserRepo(session)


async def get_device_repository(session: AsyncSession = Depends(get_session)):
    return PostgresDeviceRepo(session)


async def get_department_repository(session: AsyncSession = Depends(get_session)):
    return PostgresDepartmentRepo(session)
