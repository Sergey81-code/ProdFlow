from sqlalchemy.ext.asyncio import AsyncSession

from app.operation_stages.repo_interface import IOperationStageRepository


class PostgresOperationStageRepo(IOperationStageRepository):
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session
