from typing import Any
from uuid import UUID
from app.operation_stages.models import OperationStage
from app.operation_stages.repo_interface import IOperationStageRepository


class OperationStageService:
    def __init__(self, repo: IOperationStageRepository):
        self._repo: IOperationStageRepository = repo

    async def create_operation_stage_in_db(
        self, operation_stage_info: dict[str, Any]
    ) -> OperationStage: ...

    async def get_operation_stages(
        self, id: UUID | None = None
    ) -> list[OperationStage]: ...

    async def delete_operation_stage_by_id(self, id: UUID) -> UUID: ...

    async def update_operation_stage(
        self,
        operation_stage: OperationStage,
        operation_stage_update_info: dict[str, Any],
    ) -> OperationStage: ...
