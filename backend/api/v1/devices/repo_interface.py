from abc import ABC, abstractmethod
from uuid import UUID

from api.v1.devices.schemas import CreateDevice, Device, UpdateDevice


class DeviceRepoInterface(ABC):

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Device:
        pass

    @abstractmethod
    async def create(self, info: CreateDevice) -> Device:
        pass

    @abstractmethod
    async def update(self, device: Device, info: UpdateDevice):
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> UUID:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> list[Device]:
        pass

    @abstractmethod
    async def get_all(self) -> list[Device]:
        pass

    @abstractmethod
    async def get_by_android_id(self, android_id: UUID) -> Device:
        pass
