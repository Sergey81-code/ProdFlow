from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.devices.models import Device


class IDeviceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Device | None:
        pass

    @abstractmethod
    async def create(self, device_info: dict[str, Any]) -> Device:
        pass

    @abstractmethod
    async def update(self, device: Device, device_info: dict[str, Any]) -> Device:
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> UUID:
        pass

    @abstractmethod
    async def get_by_name(
        self, name: str, exact_match: bool = False, case_sensitive: bool = False
    ) -> list[Device]:
        pass

    @abstractmethod
    async def get_all(self) -> list[Device]:
        pass

    @abstractmethod
    async def get_by_android_id(self, android_id: str) -> Device | None:
        pass
