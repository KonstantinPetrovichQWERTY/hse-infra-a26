import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Device, Measurement, User
from src.routes.devices.schemas import DeviceSchema, StatsValues
from src.routes.users.abstract_data_storage import UserDataStorage
from src.routes.users.exceptions import (
    UserAlreadyExistException,
    UserNotFoundException,
)
from src.routes.users.schemas import (
    DeviceStats,
    FullUserSchema,
    PartialUserSchema,
    UserAggregatedStatsResponse,
    UserDeviceStatsResponse,
    UserWithDevicesSchema,
)


class UserPostgreDAO(UserDataStorage):
    async def create_user(
        self,
        session: AsyncSession,
        user_data: PartialUserSchema,
    ) -> FullUserSchema:
        existing_user = await session.execute(
            select(User).where(User.name == user_data.name)
        )
        if existing_user.scalar_one_or_none():
            raise UserAlreadyExistException()

        new_user = User(name=user_data.name)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return FullUserSchema(id=new_user.id, name=new_user.name)

    async def get_user(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> UserWithDevicesSchema:
        stmt = (
            select(User).where(User.id == user_id).options(selectinload(User.devices))
        )

        user = (await session.scalars(stmt)).first()

        if not user:
            raise UserNotFoundException()

        return UserWithDevicesSchema(
            id=user.id,
            name=user.name,
            devices=[
                DeviceSchema(id=device.id, serial_number=device.serial_number)
                for device in user.devices
            ],
        )

    async def get_all_users(
        self,
        session: AsyncSession,
    ) -> list[FullUserSchema]:
        result = await session.execute(select(User))
        users = result.scalars().all()

        return [FullUserSchema(id=user.id, name=user.name) for user in users]

    async def _get_user_measurements(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> tuple[
        User, list[Device], dict[uuid.UUID, list[Measurement]], list[Measurement]
    ]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.devices).selectinload(Device.measurements))
        )

        user = (await session.scalars(stmt)).first()
        if not user:
            raise UserNotFoundException()

        device_measurements_map = {}
        all_measurements = []

        for device in user.devices:
            device_measurements = [
                m
                for m in device.measurements
                if (not start_date or m.timestamp >= start_date)
                and (not end_date or m.timestamp <= end_date)
            ]
            device_measurements_map[device.id] = device_measurements
            all_measurements.extend(device_measurements)

        return user, user.devices, device_measurements_map, all_measurements

    async def _calculate_stats(self, values: list[float]) -> StatsValues:
        if not values:
            return StatsValues(min=0.0, max=0.0, count=0, sum=0.0, median=0.0)

        sorted_values = sorted(values)
        count = len(sorted_values)
        return StatsValues(
            min=min(sorted_values),
            max=max(sorted_values),
            count=count,
            sum=sum(sorted_values),
            median=(
                sorted_values[count // 2]
                if count % 2
                else (sorted_values[count // 2 - 1] + sorted_values[count // 2]) / 2
            ),
        )

    async def get_user_aggregated_stats(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> UserAggregatedStatsResponse:
        user, devices, _, all_measurements = await self._get_user_measurements(
            session, user_id, start_date, end_date
        )

        return UserAggregatedStatsResponse(
            user_id=user_id,
            total_devices=len(devices),
            total_measurements=len(all_measurements),
            period={"start": start_date, "end": end_date},
            stats={
                "x": await self._calculate_stats([m.x for m in all_measurements]),
                "y": await self._calculate_stats([m.y for m in all_measurements]),
                "z": await self._calculate_stats([m.z for m in all_measurements]),
            },
        )

    async def get_user_devices_stats(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> UserDeviceStatsResponse:
        (
            user,
            devices,
            device_measurements_map,
            all_measurements,
        ) = await self._get_user_measurements(session, user_id, start_date, end_date)

        devices_stats = []
        for device in devices:
            measurements = device_measurements_map.get(device.id, [])
            devices_stats.append(
                DeviceStats(
                    device_id=device.id,
                    stats={
                        "x": await self._calculate_stats([m.x for m in measurements]),
                        "y": await self._calculate_stats([m.y for m in measurements]),
                        "z": await self._calculate_stats([m.z for m in measurements]),
                    },
                )
            )

        return UserDeviceStatsResponse(
            user_id=user_id,
            total_devices=len(devices),
            total_measurements=len(all_measurements),
            period={"start": start_date, "end": end_date},
            devices=devices_stats,
        )


dao = UserPostgreDAO()
