from abc import ABC, abstractmethod
from uuid import UUID

from api.v1.users.schemas import CreateUser, UpdateUser, User


class UserRepoInterface(ABC):

    @abstractmethod
    async def get_by_id(self, id: UUID) -> User:
        pass

    @abstractmethod
    async def create(self, info: CreateUser) -> User:
        pass

    @abstractmethod
    async def update(self, user: User, info: UpdateUser):
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> UUID:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> list[User]:
        pass

    @abstractmethod
    async def get_all(self) -> list[User]:
        pass

    @abstractmethod
    async def get_user_permissions(self, id) -> list[str]:
        pass
