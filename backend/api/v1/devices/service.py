from uuid import UUID
from api.core.exceptions import AppExceptions
from api.v1.devices.repo_interface import DeviceRepoInterface
from api.v1.devices.schemas import CreateDevice, Device
from db.db_exceptions import DBException


class DeviceService:
    def __init__(self, device_repository_interface: DeviceRepoInterface):
        self._repo: DeviceRepoInterface = device_repository_interface

    async def get_device_by_id(self, device_id: UUID) -> Device:
        try:
            return await self._repo.get_by_id(device_id)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def create_device_in_database(self, device_info: CreateDevice) -> Device:
        try:
            return await self._repo.create(device_info)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def update_device(self, device: Device, body: CreateDevice) -> Device:
        try:
            return await self._repo.update(device, body)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def delete_device_by_id(self, device_id: UUID) -> UUID:
        try:
            return await self._repo.delete(device_id)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def get_device_by_name_or_all(self, device_name: str) -> list[Device]:
        try:
            if device_name:
                return await self._repo.get_by_name(device_name)
            return await self._repo.get_all()
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def get_device_by_android_id(self, android_id: UUID) -> Device:
        try:
            return await self._repo.get_by_android_id(android_id)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")
