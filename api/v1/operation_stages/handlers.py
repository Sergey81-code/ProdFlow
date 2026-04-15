from uuid import UUID
from fastapi import APIRouter, Depends

from api.core.dependencies.jwt_access import permission_required
from api.core.dependencies.services import get_operation_stage_service
from api.v1.operation_stages.schemas import (
    CreateOperationStage,
    ShowOperationStage,
    UpdateOperationStage,
)
from app.operation_stages.service import OperationStageService
from config.permissions import Permissions


router = APIRouter()


@router.post(
    "/",
    response_model=ShowOperationStage,
    dependencies=[permission_required([Permissions.DELETE_DEPARTMENT])],
)
async def create_operation_stage(
    operation_stage_info: CreateOperationStage,
    service: OperationStageService = Depends(get_operation_stage_service),
) -> ShowOperationStage:
    return await service.create_operation_stage_in_db(operation_stage_info)


@router.get(
    "/{operation_stage_id}",
    response_model=ShowOperationStage,
    dependencies=[permission_required([Permissions.GET_OPERATION_STAGES])],
)
async def get_operation_stage_by_id(
    operation_stage_id: UUID,
    service: OperationStageService = Depends(get_operation_stage_service),
) -> ShowOperationStage:
    operation_stages = await service.get_operation_stages(id=operation_stage_id)
    return operation_stages[0]


@router.get(
    "/",
    response_model=list[ShowOperationStage],
    dependencies=[permission_required([Permissions.GET_OPERATION_STAGES])],
)
async def get_operation_stages_by_name_or_all(
    operation_stage_name: str | None = None,
    service: OperationStageService = Depends(get_operation_stage_service),
) -> list[ShowOperationStage]:
    if operation_stage_name:
        return await service.get_operation_stages(name=operation_stage_name)
    return await service.get_operation_stages()


@router.delete(
    "/{operation_stage_id}",
    dependencies=[permission_required([Permissions.DELETE_OPERATION_STAGE])],
)
async def delete_operation_stage(
    operation_stage_id: UUID,
    service: OperationStageService = Depends(get_operation_stage_service),
) -> UUID:
    return await service.delete_operation_stage_by_id(operation_stage_id)


@router.patch(
    "/{operation_stage_id}",
    response_model=ShowOperationStage,
    dependencies=[permission_required([Permissions.UPDATE_OPERATION_STAGE])],
)
async def update_operation_stage(
    operation_stage_id: UUID,
    operation_stage_update_info: UpdateOperationStage,
    service: OperationStageService = Depends(get_operation_stage_service),
) -> ShowOperationStage:
    operation_stage = (await service.get_operation_stages(id=operation_stage_id))[0]
    return await service.update_operation_stage(
        operation_stage, operation_stage_update_info
    )
