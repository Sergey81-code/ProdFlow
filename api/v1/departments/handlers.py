from uuid import UUID
from fastapi import APIRouter, Depends

from api.core.dependencies.jwt_access import permission_required
from api.core.dependencies.services import get_department_service
from api.v1.departments.schemas import (
    CreateDepartment,
    ShowDepartment,
    UpdateDepartment,
)
from api.v1.departments.service import DepartmentService
from config.permissions import Permissions


router = APIRouter()


@router.post(
    "/",
    response_model=ShowDepartment,
    dependencies=[permission_required([Permissions.CREATE_DEPARTMENT])],
)
async def create_department(
    body: CreateDepartment, service: DepartmentService = Depends(get_department_service)
) -> ShowDepartment:
    return await service.create_department_in_database(body)


@router.get(
    "/code/{department_code}",
    response_model=ShowDepartment,
    dependencies=[permission_required([Permissions.GET_DEPARTMENTS])],
)
async def get_department_by_code(
    department_code: str, service: DepartmentService = Depends(get_department_service)
) -> ShowDepartment:
    departments = await service.get_departments(code=department_code)
    return departments[0]


@router.get("/", dependencies=[permission_required([Permissions.GET_DEPARTMENTS])])
async def get_departments_by_name_or_all(
    department_name: str | None = None,
    service: DepartmentService = Depends(get_department_service),
) -> list[ShowDepartment]:
    if department_name:
        return await service.get_departments(name=department_name)
    return await service.get_departments()


@router.get(
    "/{department_id}",
    response_model=ShowDepartment,
    dependencies=[permission_required([Permissions.GET_DEPARTMENTS])],
)
async def get_department_by_id(
    department_id: UUID, service: DepartmentService = Depends(get_department_service)
) -> ShowDepartment:
    departments = await service.get_departments(id=department_id)
    return departments[0]


@router.patch(
    "/{department_id}",
    response_model=ShowDepartment,
    dependencies=[permission_required([Permissions.UPDATE_DEPARTMENT])],
)
async def update_department(
    department_id: UUID,
    body: UpdateDepartment,
    service: DepartmentService = Depends(get_department_service),
) -> ShowDepartment:
    department = (await service.get_departments(id=department_id))[0]
    return await service.update_department(department, body)


@router.delete(
    "/{department_id}",
    dependencies=[permission_required([Permissions.DELETE_DEPARTMENT])],
)
async def delete_department(
    department_id: UUID, service: DepartmentService = Depends(get_department_service)
) -> UUID:
    return await service.delete_department_by_id(department_id)
