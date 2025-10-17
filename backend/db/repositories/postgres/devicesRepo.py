from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.devices.repo_interface import DeviceRepoInterface
from db.models import Device as DeviceModel
from api.v1.devices.schemas import CreateDevice, UpdateDevice, Device


class PostgresDeviceRepo(DeviceRepoInterface):
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

    async def get_by_name(self, name: str) -> list[Device]:
        stmt = select(DeviceModel).where(DeviceModel.name.ilike(f"%{name}%"))
        result = await self._session.execute(stmt)
        devices = result.scalars().all()
        return [Device.model_validate(d) for d in devices]

    async def get_all(self) -> list[Device]:
        stmt = select(DeviceModel)
        result = await self._session.execute(stmt)
        devices = result.scalars().all()
        return [Device.model_validate(d) for d in devices]

    async def get_by_android_id(self, android_id: UUID) -> Device | None:
        stmt = select(DeviceModel).where(DeviceModel.android_id == android_id)
        result = await self._session.execute(stmt)
        device = result.scalar_one_or_none()
        return Device.model_validate(device) if device else None
