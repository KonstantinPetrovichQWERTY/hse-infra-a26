import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PartialDeviceSchema(BaseModel):
    """Base schema for device creation."""

    serial_number: str = Field(
        min_length=3,
        max_length=30,
        title="Serial number",
    )


class DeviceSchema(PartialDeviceSchema):
    """Complete device representation including system-generated ID.

    Extends PartialDeviceSchema with:
        id: Universally unique identifier for the device.
    """

    id: uuid.UUID = Field(title="Device ID")

    class Config:
        from_attributes = True


class MeasurementCreateSchema(BaseModel):
    """Schema for creating new measurement records."""

    x: float = Field(title="X-axis measurement")
    y: float = Field(title="Y-axis measurement")
    z: float = Field(title="Z-axis measurement")


class PartialUserSchema(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        title="User name",
    )


class UserSchema(PartialUserSchema):
    id: uuid.UUID = Field(title="User ID")

    class Config:
        from_attributes = True


class MeasurementSchema(MeasurementCreateSchema):
    """Complete measurement record including metadata."""

    id: uuid.UUID = Field(title="Measurement ID")
    device_id: uuid.UUID = Field(title="Device ID")
    timestamp: datetime = Field(title="Measurement timestamp")

    class Config:
        from_attributes = True


class StatsValues(BaseModel):
    """Statistical summary for a set of measurement values."""

    min: float = Field(title="Minimum value")
    max: float = Field(title="Maximum value")
    count: int = Field(title="Number of values")
    sum: float = Field(title="Sum of values")
    median: float = Field(title="Median value")


class DeviceStatsResponse(BaseModel):
    """Comprehensive statistical analysis for a device's measurements."""

    device_id: uuid.UUID = Field(title="Device ID")
    x: StatsValues = Field(title="X-axis statistics")
    y: StatsValues = Field(title="Y-axis statistics")
    z: StatsValues = Field(title="Z-axis statistics")
    period: dict[str, datetime | None] = Field(
        title="Measurement period",
    )


class DeviceWithUsersSchema(DeviceSchema):
    """Extended device information including associated users."""

    users: list[UserSchema] = Field(default_factory=list, title="Device users")
