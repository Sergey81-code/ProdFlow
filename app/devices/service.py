from typing import Any
from uuid import UUID

from app.core.exceptions.api_exceptions import ApiExceptions
from app.devices.models import Device
from app.devices.repo_interface import IDeviceRepository
from app.core.exceptions.db_exceptions import DbExceptions


class DeviceService:
    def __init__(self, device_repository_interface: IDeviceRepository):
        self._repo: IDeviceRepository = device_repository_interface

    async def get_device_by_id(self, device_id: UUID) -> Device:
        try:
            device: Device | None = await self._repo.get_by_id(device_id)
            if device is None:
                raise ApiExceptions.not_found_exception("Device with this id not found")
            return device
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def create_device_in_database(self, device_info: dict[str, Any]) -> Device:
        try:
            if (
                await self._repo.get_by_name(
                    device_info["name"], exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise ApiExceptions.bad_request_exception(
                    f"Device with name {device_info["name"]} already exists"
                )
            if (
                await self._repo.get_by_android_id(device_info["android_id"])
                is not None
            ):
                raise ApiExceptions.bad_request_exception(
                    f"Device with android_id {device_info["android_id"]} already exists"
                )
            return await self._repo.create(device_info)
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def update_device(
        self, device: Device, device_info: dict[str, Any]
    ) -> Device:
        try:
            if not device_info:
                raise ApiExceptions.validation_exception(
                    "At least one parameter must be defined"
                )
            if (
                device_info.get("name")
                and device_info["name"] != device.name
                and (
                    await self._repo.get_by_name(
                        device_info["name"], exact_match=True, case_sensitive=False
                    )
                    != []
                )
            ):
                raise ApiExceptions.bad_request_exception(
                    f"Device with name {device_info["name"]} already exists."
                )
            if (
                device_info.get("android_id")
                and device_info["android_id"] != device.android_id
                and await self._repo.get_by_android_id(device_info["android_id"])
                is not None
            ):
                raise ApiExceptions.bad_request_exception(
                    "Device with this android_id already exists"
                )
            return await self._repo.update(device, device_info)
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def delete_device_by_id(self, device_id: UUID) -> UUID:
        try:
            if await self._repo.get_by_id(device_id) is None:
                raise ApiExceptions.not_found_exception("Device with this id not found")
            return await self._repo.delete(device_id)
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def get_device_by_name_or_all(self, device_name: str) -> list[Device]:
        try:
            if device_name:
                return await self._repo.get_by_name(device_name)
            return await self._repo.get_all()
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def get_device_by_android_id(self, android_id: str) -> Device:
        try:
            device = await self._repo.get_by_android_id(android_id)
            if not device:
                raise ApiExceptions.not_found_exception(
                    f"Device with this android id {android_id} not found"
                )
            return device
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")
