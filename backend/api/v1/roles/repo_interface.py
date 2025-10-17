from abc import ABC, abstractmethod
from uuid import UUID

from api.v1.roles.schemas import CreateRole, Role, UpdateRole


class RoleRepoInterface(ABC):

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Role:
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
    async def get_by_name(self, name: str) -> list[Role]:
        pass

    @abstractmethod
    async def get_all(self) -> list[Role]:
        pass
