from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.roles.models import Role


class IRoleRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Role | None:
        pass

    @abstractmethod
    async def create(self, role_info: dict[str, Any]) -> Role:
        pass

    @abstractmethod
    async def update(self, role: Role, role_info: dict[str, Any]):
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> UUID:
        pass

    @abstractmethod
    async def get_by_name(
        self, name: str, exact_match: bool = False, case_sensitive: bool = False
    ) -> list[Role]:
        pass

    @abstractmethod
    async def get_all(self) -> list[Role]:
        pass
