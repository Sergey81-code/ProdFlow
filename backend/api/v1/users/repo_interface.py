from abc import ABC, abstractmethod
from uuid import UUID

from api.v1.users.schemas import CreateUser, UpdateUser, User


class IUserRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id: UUID) -> User | None:
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
    async def get_by_username(
        self, name: str, exact_match: bool = False, case_sensitive: bool = False
    ) -> list[User]:
        pass

    @abstractmethod
    async def get_by_person_name_fields(
        self, name: str, exact_match: bool = False, case_sensitive: bool = False
    ) -> list[User]:
        pass

    @abstractmethod
    async def get_all(self) -> list[User]:
        pass

    @abstractmethod
    async def get_user_permissions(self, id) -> list[str]:
        pass
