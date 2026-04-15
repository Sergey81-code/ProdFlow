from uuid import UUID
from pydantic import BaseModel


class OperationStage(BaseModel):
    id: UUID
    name: str
