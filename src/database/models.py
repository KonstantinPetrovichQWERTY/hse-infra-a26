import uuid
from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, Column, DateTime, Float, ForeignKey, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# I do not like this format, but it mentioned in SQLAlchemy doc.
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many
user_device_association = Table(
    "user_device_association",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("device_id", UUID(as_uuid=True), ForeignKey("devices.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255))

    devices: Mapped[list["Device"]] = relationship(
        secondary=user_device_association, back_populates="users"
    )


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,
    )

    serial_number: Mapped[str] = mapped_column(String(30), unique=True)

    users: Mapped[list["User"]] = relationship(
        secondary=user_device_association, back_populates="devices"
    )
    measurements: Mapped[list["Measurement"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id"), index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    z: Mapped[float] = mapped_column(Float)

    device: Mapped["Device"] = relationship(back_populates="measurements")
