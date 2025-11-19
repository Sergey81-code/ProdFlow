from uuid import UUID

from api.core.exceptions import AppExceptions
from api.v1.devices.repo_interface import IDeviceRepository
from api.v1.devices.schemas import CreateDevice, Device
from db.db_exceptions import DBException


class DeviceService:
    def __init__(self, device_repository_interface: IDeviceRepository):
        self._repo: IDeviceRepository = device_repository_interface

    async def get_device_by_id(self, device_id: UUID) -> Device:
        try:
            device: Device | None = await self._repo.get_by_id(device_id)
            if device is None:
                raise AppExceptions.not_found_exception("Device with this id not found")
            return device
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def create_device_in_database(self, device_info: CreateDevice) -> Device:
        try:
            if (
                await self._repo.get_by_name(
                    device_info.name, exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise AppExceptions.bad_request_exception(
                    f"Device with name {device_info.name} already exists"
                )
            if await self._repo.get_by_android_id(device_info.android_id) is not None:
                raise AppExceptions.bad_request_exception(
                    f"Device with android_id {device_info.android_id} already exists"
                )
            return await self._repo.create(device_info)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def update_device(self, device: Device, body: CreateDevice) -> Device:
        try:
            if not body.model_dump(exclude_none=True):
                raise AppExceptions.validation_exception(
                    "At least one parameter must be defined"
                )
            if body.name and (
                await self._repo.get_by_name(
                    body.name, exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise AppExceptions.bad_request_exception(
                    f"Device with name {body.name} already exists."
                )
            if (
                body.android_id
                and await self._repo.get_by_android_id(body.android_id) is not None
            ):
                raise AppExceptions.bad_request_exception(
                    "Device with this android_id already exists"
                )
            return await self._repo.update(device, body)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def delete_device_by_id(self, device_id: UUID) -> UUID:
        try:
            if await self._repo.get_by_id(device_id) is None:
                raise AppExceptions.not_found_exception("Device with this id not found")
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
