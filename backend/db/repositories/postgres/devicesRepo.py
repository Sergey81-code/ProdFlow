from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.devices.repo_interface import IDeviceRepository
from api.v1.devices.schemas import CreateDevice, Device, UpdateDevice
from db.models import Device as DeviceModel


class PostgresDeviceRepo(IDeviceRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: UUID) -> Device | None:
        stmt = select(DeviceModel).where(DeviceModel.id == id)
        result = await self._session.execute(stmt)
        device = result.scalar_one_or_none()
        return Device.model_validate(device) if device else None

    async def create(self, info: CreateDevice) -> Device:
        device = DeviceModel(**info.model_dump(exclude_none=True))
        self._session.add(device)
        await self._session.commit()
        await self._session.refresh(device)
        return Device.model_validate(device)

    async def update(self, device: Device, info: UpdateDevice) -> Device:
        stmt = (
            update(DeviceModel)
            .where(DeviceModel.id == device.id)
            .values(**info.model_dump(exclude_none=True))
            .returning(DeviceModel)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        updated_device = result.scalar_one()
        return Device.model_validate(updated_device)

    async def delete(self, id: UUID) -> UUID:
        stmt = delete(DeviceModel).where(DeviceModel.id == id).returning(DeviceModel.id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        deleted_id = result.scalar_one_or_none()
        return deleted_id

    async def get_by_name(
        self,
        name: str,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> list[Device]:
        if exact_match:
            pattern = name
            filter_expr = (
                DeviceModel.name == pattern
                if case_sensitive
                else func.lower(DeviceModel.name) == pattern.lower()
            )
        else:
            pattern = f"%{name}%"
            filter_expr = (
                DeviceModel.name.like(pattern)
                if case_sensitive
                else DeviceModel.name.ilike(pattern)
            )

        stmt = select(DeviceModel).where(filter_expr)
        result = await self._session.execute(stmt)
        return [Device.model_validate(d) for d in result.scalars().all()]

    async def get_all(self) -> list[Device]:
        stmt = select(DeviceModel)
        result = await self._session.execute(stmt)
        devices = result.scalars().all()
        return [Device.model_validate(d) for d in devices]

    async def get_by_android_id(self, android_id: str) -> Device | None:
        stmt = select(DeviceModel).where(
            func.lower(DeviceModel.android_id) == android_id.lower()
        )
        result = await self._session.execute(stmt)
        device = result.scalar_one_or_none()
        return Device.model_validate(device) if device else None
