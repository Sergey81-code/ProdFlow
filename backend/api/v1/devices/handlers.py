from uuid import UUID

from fastapi import APIRouter, Depends

from api.core.dependencies.jwt_access import permission_required
from api.core.dependencies.services import get_device_service
from api.v1.devices.schemas import CreateDevice, ShowDevice, UpdateDevice
from api.v1.devices.service import DeviceService
from config.permissions import Permissions

router = APIRouter()


@router.get(
    "/{device_id}",
    response_model=ShowDevice,
    dependencies=[permission_required([Permissions.GET_DEVICES])],
)
async def get_device(
    device_id: UUID,
    device_service: DeviceService = Depends(get_device_service),
) -> ShowDevice:
    return await device_service.get_device_by_id(device_id)


@router.post(
    "/",
    response_model=ShowDevice,
    dependencies=[permission_required([Permissions.CREATE_DEVICE])],
)
async def create_device(
    body: CreateDevice,
    device_service: DeviceService = Depends(get_device_service),
) -> ShowDevice:
    return await device_service.create_device_in_database(body)


@router.patch(
    "/{device_id}",
    response_model=ShowDevice,
    dependencies=[permission_required([Permissions.UPDATE_DEVICE])],
)
async def update_device(
    device_id: UUID,
    body: UpdateDevice,
    device_service: DeviceService = Depends(get_device_service),
) -> ShowDevice:
    device = await device_service.get_device_by_id(device_id)
    return await device_service.update_device(device, body)


@router.delete(
    "/{device_id}",
    dependencies=[permission_required([Permissions.DELETE_DEVICE])],
)
async def delete_device(
    device_id: UUID,
    device_service: DeviceService = Depends(get_device_service),
) -> UUID:
    return await device_service.delete_device_by_id(device_id)


@router.get(
    "/",
    response_model=list[ShowDevice],
    dependencies=[permission_required([Permissions.GET_DEVICES])],
)
async def get_devices_by_name_or_all(
    device_name: str | None = None,
    device_service: DeviceService = Depends(get_device_service),
) -> list[ShowDevice]:
    return await device_service.get_device_by_name_or_all(device_name)


@router.get(
    "/",
    response_model=list[ShowDevice],
    dependencies=[permission_required([Permissions.GET_DEVICES])],
)
async def get_devices_by_android_id(
    device_android_id: UUID | None = None,
    device_service: DeviceService = Depends(get_device_service),
) -> ShowDevice:
    return await device_service.get_device_by_android_id(device_android_id)
