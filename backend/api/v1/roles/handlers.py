from uuid import UUID
from fastapi import APIRouter, Depends

from api.core.dependencies.jwt_access import permission_required
from api.core.dependencies.services import get_role_service
from api.v1.roles.schemas import CreateRole, ShowRole, UpdateRole
from api.v1.roles.service import RoleService
from config.permissions import Premissions


router = APIRouter()


@router.get(
    "/{role_id}",
    response_model=ShowRole,
    dependencies=[permission_required([Premissions.GET_ROLES])],
)
async def get_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
) -> ShowRole:
    return await role_service.get_role_by_id(role_id)


@router.post(
    "/",
    response_model=ShowRole,
    dependencies=[permission_required([Premissions.CREATE_ROLE])],
)
async def create_role(
    body: CreateRole,
    role_service: RoleService = Depends(get_role_service),
) -> ShowRole:
    return await role_service.create_role_in_database(body)


@router.patch(
    "/{role_id}",
    response_model=ShowRole,
    dependencies=[permission_required([Premissions.UPDATE_ROLE])],
)
async def update_role(
    role_id: UUID,
    body: UpdateRole,
    role_service: RoleService = Depends(get_role_service),
) -> ShowRole:
    role = await role_service.get_role_by_id(role_id)
    return await role_service.update_role(role, body)


@router.delete(
    "/{role_id}",
    dependencies=[permission_required([Premissions.DELETE_ROLE])],
)
async def delete_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
) -> list[UUID]:
    return await role_service.delete_role_by_id(role_id)


@router.get(
    "/",
    response_model=list[ShowRole],
    dependencies=[permission_required([Premissions.GET_ROLES])],
)
async def get_roles_by_name_or_all(
    role_name: str | None = None,
    role_service: RoleService = Depends(get_role_service),
) -> ShowRole:
    return await role_service.get_role_by_name_or_all(role_name)
