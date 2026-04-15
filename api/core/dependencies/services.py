from typing import TYPE_CHECKING
from fastapi import Depends

from api.core.dependencies.integrations import get_erm_source
from api.core.dependencies.repositories import (
    get_device_repository,
    get_operation_stage_repository,
    get_prod_journal_repository,
    get_prod_journal_route_record_repository,
    get_prod_journal_route_repository,
    get_prod_order_repository,
    get_prod_route_repository,
    get_role_repository,
    get_user_repository,
    get_department_repository,
)
from api.v1.auth.service import AuthService
from app.devices.service import DeviceService
from app.operation_stages.service import OperationStageService
from app.production_orders.service import ProductionOrderService
from app.roles.service import RoleService
from app.users.service import UserService
from app.departments.service import DepartmentService
from integrations.ERM.service import ERMProdOrderLoadService

if TYPE_CHECKING:
    from app.devices.repo_interface import IDeviceRepository
    from app.operation_stages.repo_interface import IOperationStageRepository
    from app.production_journal.repo_interface import IProdJournalRepository
    from app.production_journal_routes.repo_interface import IProdJournalRouteRepository
    from app.production_orders.repo_interface import IProdOrderRepository
    from app.production_routes.repo_interface import IProdRouteRepository
    from app.roles.repo_interface import IRoleRepository
    from app.users.repo_interface import IUserRepository
    from app.departments.repo_interface import IDepartmentRepository
    from integrations.ERM.ports.source import ERMProdOrderSourcePort
    from app.production_journal_route_records.repo_interface import (
        IProdJournalRouteRecordRepository,
    )


async def get_role_service(
    repo: "IRoleRepository" = Depends(get_role_repository),
):
    return RoleService(repo)


async def get_user_service(
    repo: "IUserRepository" = Depends(get_user_repository),
    role_repo: "IRoleRepository" = Depends(get_role_repository),
    department_repo: "IDepartmentRepository" = Depends(get_department_repository),
):
    return UserService(repo, role_repo, department_repo)


async def get_device_service(
    repo: "IDeviceRepository" = Depends(get_device_repository),
):
    return DeviceService(repo)


async def get_auth_service(
    repo: "IDeviceRepository" = Depends(get_user_repository),
):
    return AuthService(repo)


async def get_department_service(
    repo: "IDepartmentRepository" = Depends(get_department_repository),
):
    return DepartmentService(repo)


async def get_operation_stage_service(
    repo: "IOperationStageRepository" = Depends(get_operation_stage_repository),
):
    return OperationStageService(repo)


async def get_erm_production_service(
    erm_source: "ERMProdOrderSourcePort" = Depends(get_erm_source),
    prod_order_repo: "IProdOrderRepository" = Depends(get_prod_order_repository),
    prod_route_repo: "IProdRouteRepository" = Depends(get_prod_route_repository),
    prod_journal_repo: "IProdJournalRepository" = Depends(get_prod_journal_repository),
    prod_journal_route_repo: "IProdJournalRouteRepository" = Depends(
        get_prod_journal_route_repository
    ),
    user_repo: "IUserRepository" = Depends(get_user_repository),
    prod_journal_route_record_repository: "IProdJournalRouteRecordRepository" = Depends(
        get_prod_journal_route_record_repository
    ),
):
    return ERMProdOrderLoadService(
        erm_source_port=erm_source,
        order_repo=prod_order_repo,
        route_repo=prod_route_repo,
        journal_repo=prod_journal_repo,
        journal_route_repo=prod_journal_route_repo,
        user_repo=user_repo,
        journal_route_record_repo=prod_journal_route_record_repository,
    )


async def get_production_service(
    prod_order_repo: "IProdOrderRepository" = Depends(get_prod_order_repository),
    prod_route_repo: "IProdRouteRepository" = Depends(get_prod_route_repository),
    prod_journal_repo: "IProdJournalRepository" = Depends(get_prod_journal_repository),
    prod_journal_route_repo: "IProdJournalRouteRepository" = Depends(
        get_prod_journal_route_repository
    ),
    prod_journal_route_record_repository: "IProdJournalRouteRecordRepository" = Depends(
        get_prod_journal_route_record_repository
    ),
    user_repo: "IUserRepository" = Depends(get_user_repository),
):
    return ProductionOrderService(
        order_repo=prod_order_repo,
        route_repo=prod_route_repo,
        journal_repo=prod_journal_repo,
        journal_route_repo=prod_journal_route_repo,
        journal_route_record_repo=prod_journal_route_record_repository,
        user_repo=user_repo,
    )
