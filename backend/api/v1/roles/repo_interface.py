from abc import ABC, abstractmethod
from uuid import UUID

from api.v1.roles.schemas import CreateRole, Role, UpdateRole


class IRoleRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Role | None:
        pass

    @abstractmethod
    async def create(self, info: CreateRole) -> Role:
        pass

    @abstractmethod
    async def update(self, role: Role, info: UpdateRole):
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
