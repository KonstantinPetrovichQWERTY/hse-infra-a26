import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Device, Measurement, User
from src.routes.devices.abstract_data_storage import DeviceDataStorage
from src.routes.devices.exceptions import (
    DeviceNotFoundException,
    DeviceSerialNumberException,
    MeasurementNotFoundException,
)
from src.routes.devices.schemas import (
    DeviceSchema,
    DeviceStatsResponse,
    DeviceWithUsersSchema,
    MeasurementCreateSchema,
    MeasurementSchema,
    PartialDeviceSchema,
    UserSchema,
)
from src.routes.users.exceptions import UserAlreadyExistException, UserNotFoundException


class DevicePostgreDAO(DeviceDataStorage):
    async def get_device(
        self,
        session: AsyncSession,
        device_id: uuid.UUID,
    ) -> DeviceWithUsersSchema:
        stmt = (
            select(Device)
            .where(Device.id == device_id)
            .options(selectinload(Device.users))
        )

        device = (await session.scalars(stmt)).first()

        if not device:
            raise DeviceNotFoundException()

        result = DeviceWithUsersSchema(
            id=device.id,
            serial_number=device.serial_number,
            users=[UserSchema(name=user.name, id=user.id) for user in device.users],
        )

        return result

    async def register_new_device(
        self,
        session: AsyncSession,
        device_data: PartialDeviceSchema,
    ) -> DeviceSchema:

        existing_device = await session.execute(
            select(Device).where(Device.serial_number == device_data.serial_number)
        )
        if existing_device.scalar_one_or_none():
            raise DeviceSerialNumberException()

        new_device = Device(
            serial_number=device_data.serial_number,
        )

        session.add(new_device)
        await session.commit()
        await session.refresh(new_device)

        result = DeviceSchema(
            serial_number=new_device.serial_number,
            id=new_device.id,
        )

        return result

    async def get_all_devices(self, session: AsyncSession) -> list[DeviceSchema]:
        result = await session.execute(select(Device))
        devices = result.scalars().all()

        if not devices:
            raise DeviceNotFoundException()

        return [
            DeviceSchema(id=device.id, serial_number=device.serial_number)
            for device in devices
        ]

    async def get_device_stats(
        self,
        session: AsyncSession,
        device_id: uuid.UUID,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> DeviceStatsResponse:
        device = await session.get(Device, device_id)

        if not device:
            raise DeviceNotFoundException()

        query = select(Measurement).where(Measurement.device_id == device_id)
        if start_date:
            query = query.where(Measurement.timestamp >= start_date)
        if end_date:
            query = query.where(Measurement.timestamp <= end_date)

        result = await session.execute(query)
        measurements = result.scalars().all()

        if not measurements:
            raise MeasurementNotFoundException()

        x_values = [m.x for m in measurements]
        y_values = [m.y for m in measurements]
        z_values = [m.z for m in measurements]

        def calculate_stats(values):
            sorted_values = sorted(values)
            count = len(sorted_values)
            return {
                "min": min(sorted_values),
                "max": max(sorted_values),
                "count": count,
                "sum": sum(sorted_values),
                "median": (
                    sorted_values[count // 2]
                    if count % 2
                    else (sorted_values[count // 2 - 1] + sorted_values[count // 2]) / 2
                ),
            }

        return DeviceStatsResponse(
            x=calculate_stats(x_values),
            y=calculate_stats(y_values),
            z=calculate_stats(z_values),
            device_id=device_id,
            period={"start": start_date, "end": end_date},
        )

    async def add_measurement(
        self,
        session: AsyncSession,
        device_id: uuid.UUID,
        measurement_data: MeasurementCreateSchema,
    ) -> MeasurementSchema:

        device = await session.get(Device, device_id)

        if not device:
            raise DeviceNotFoundException()

        measurement = Measurement(
            device_id=device_id,
            timestamp=datetime.now(UTC),
            **measurement_data.model_dump(),
        )

        session.add(measurement)
        await session.commit()
        await session.refresh(measurement)

        result = MeasurementSchema(
            x=measurement.x,
            y=measurement.y,
            z=measurement.z,
            id=measurement.id,
            device_id=measurement.device_id,
            timestamp=measurement.timestamp,
        )

        return result

    async def get_device_measurements(
        self,
        session: AsyncSession,
        device_id: uuid.UUID,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list[MeasurementSchema]:
        query = select(Measurement).where(Measurement.device_id == device_id)

        if start_date:
            query = query.where(Measurement.timestamp >= start_date)
        if end_date:
            query = query.where(Measurement.timestamp <= end_date)

        result = await session.execute(query.order_by(Measurement.timestamp.desc()))
        measurements = result.scalars().all()

        if not measurements:
            raise MeasurementNotFoundException()

        return [
            MeasurementSchema(
                x=measurement.x,
                y=measurement.y,
                z=measurement.z,
                id=measurement.id,
                device_id=measurement.device_id,
                timestamp=measurement.timestamp,
            )
            for measurement in measurements
        ]

    async def add_user_to_device(
        self,
        session: AsyncSession,
        device_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> DeviceWithUsersSchema:
        stmt = (
            select(Device)
            .where(Device.id == device_id)
            .options(selectinload(Device.users))
        )
        device = (await session.execute(stmt)).scalar_one_or_none()

        if not device:
            raise DeviceNotFoundException()

        user = await session.get(User, user_id)
        if not user:
            raise UserNotFoundException()

        if user in device.users:
            raise UserAlreadyExistException()

        device.users.append(user)
        await session.commit()
        await session.refresh(device)

        return DeviceWithUsersSchema(
            serial_number=device.serial_number,
            id=device.id,
            users=[UserSchema(name=user.name, id=user.id) for user in device.users],
        )

    async def get_device_users(
        self,
        session: AsyncSession,
        device_id: uuid.UUID,
    ) -> list[UserSchema]:
        stmt = (
            select(Device)
            .where(Device.id == device_id)
            .options(selectinload(Device.users))
        )

        device = (await session.scalars(stmt)).first()

        if not device:
            raise DeviceNotFoundException()

        result = [UserSchema(id=user.id, name=user.name) for user in device.users]

        return result


dao = DevicePostgreDAO()
