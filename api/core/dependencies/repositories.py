from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.postgres.deviceRepo import PostgresDeviceRepo
from db.repositories.postgres.operationStageRepo import PostgresOperationStageRepo
from db.repositories.postgres.productionJournalRepo import ProdJournalRepository
from db.repositories.postgres.productionJournalRouteRecordRepo import (
    ProdJournalRouteRecordRepository,
)
from db.repositories.postgres.productionJournalRouteRepo import (
    ProdJournalRouteRepository,
)
from db.repositories.postgres.productionOrderRepo import ProdOrderRepository
from db.repositories.postgres.productionRouteRepo import ProdRoutePostgresRepository
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


async def get_operation_stage_repository(session: AsyncSession = Depends(get_session)):
    return PostgresOperationStageRepo(session)


async def get_prod_order_repository(session: AsyncSession = Depends(get_session)):
    return ProdOrderRepository(session)


async def get_prod_route_repository(session: AsyncSession = Depends(get_session)):
    return ProdRoutePostgresRepository(session)


async def get_prod_journal_repository(session: AsyncSession = Depends(get_session)):
    return ProdJournalRepository(session)


async def get_prod_journal_route_repository(
    session: AsyncSession = Depends(get_session),
):
    return ProdJournalRouteRepository(session)


async def get_prod_journal_route_record_repository(
    session: AsyncSession = Depends(get_session),
):
    return ProdJournalRouteRecordRepository(session)
