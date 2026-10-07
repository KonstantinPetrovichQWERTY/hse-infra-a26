import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.routes.devices.schemas import DeviceSchema, StatsValues


class PartialUserSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class FullUserSchema(PartialUserSchema):
    id: uuid.UUID

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)


class UserWithDevicesSchema(FullUserSchema):
    devices: list[DeviceSchema] = []


class UserAggregatedStatsResponse(BaseModel):
    user_id: uuid.UUID
    total_devices: int
    total_measurements: int
    period: dict[str, datetime | None]
    stats: dict[str, StatsValues]


class UserDeviceStatsResponse(BaseModel):
    user_id: uuid.UUID
    total_devices: int
    total_measurements: int
    period: dict[str, datetime | None]
    devices: list["DeviceStats"]


class DeviceStats(BaseModel):
    device_id: uuid.UUID
    stats: dict[str, StatsValues]
