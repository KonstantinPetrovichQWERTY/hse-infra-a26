import uuid
from datetime import datetime
from typing import Annotated

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from src.core.dependencies import DbSession
from src.routes.devices.dao import dao
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
)
from src.routes.users.exceptions import UserAlreadyExistException, UserNotFoundException
from src.routes.users.schemas import FullUserSchema

router = APIRouter(tags=["devices"])
logger = structlog.get_logger()


@router.post(
    "/api/v1/devices/register_new_device/",
    response_model=DeviceSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_new_device(
    device_data: PartialDeviceSchema,
    session: DbSession,
):
    """Register a new device in the system."""

    logger.info("register_new_device: started", device_data=device_data.model_dump())

    try:
        new_device = await dao.register_new_device(
            session=session, device_data=device_data
        )
    except DeviceSerialNumberException as e:
        logger.warning(
            "register_new_device: Device with such serial number already exists",
            serial_number=device_data.serial_number,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )

    logger.info("register_new_device: completed", device_id=new_device.id)
    return new_device


@router.get("/api/v1/devices/", response_model=list[DeviceSchema])
async def get_all_devices(session: DbSession):
    """Get list of all devices with pagination"""
    logger.info("get_all_devices: started")

    try:
        devices = await dao.get_all_devices(session=session)
    except DeviceNotFoundException as e:
        logger.warning("get_all_devices: Devices not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )

    logger.info("get_all_devices: completed", number_of_devices=len(devices))
    return devices


@router.get("/api/v1/devices/{device_id}/", response_model=DeviceWithUsersSchema)
async def get_device(device_id: uuid.UUID, session: DbSession):
    """Get device details by ID"""
    logger.info("get_device: started", device_id=device_id)

    try:
        device = await dao.get_device(session=session, device_id=device_id)
    except DeviceNotFoundException as e:
        logger.warning("get_device: Device not found", device_id=device_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )

    logger.info("get_device: completed", device_id=device_id)
    return device


@router.post(
    "/api/v1/devices/{device_id}/measurements/",
    response_model=MeasurementSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_measurement(
    device_id: uuid.UUID,
    measurement_data: MeasurementCreateSchema,
    session: DbSession,
):
    """Add new measurement for specific device"""
    logger.info("add_measurement: started", device_id=device_id)

    try:
        measurement = await dao.add_measurement(
            session=session, device_id=device_id, measurement_data=measurement_data
        )
    except DeviceNotFoundException as e:
        logger.warning("add_measurement: Device not found", device_id=device_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )

    logger.info("add_measurement: completed", measurement_id=measurement.id)
    return measurement


@router.get(
    "/api/v1/devices/{device_id}/measurements/", response_model=list[MeasurementSchema]
)
async def get_device_measurements(
    device_id: uuid.UUID,
    session: DbSession,
    start_date: Annotated[datetime | None, Query()] = None,
    end_date: Annotated[datetime | None, Query()] = None,
):
    """Get measurements for device with optional date filtering"""
    logger.info("get_device_measurements: started", device_id=device_id)

    try:
        measurements = await dao.get_device_measurements(
            session=session,
            device_id=device_id,
            start_date=start_date,
            end_date=end_date,
        )
    except MeasurementNotFoundException as e:
        logger.warning("get_device_measurements: Measurement not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )

    logger.info(
        "get_device_measurements: completed", number_of_measurements=len(measurements)
    )
    return measurements


@router.get("/api/v1/devices/{device_id}/stats/", response_model=DeviceStatsResponse)
async def get_device_stats(
    device_id: uuid.UUID,
    session: DbSession,
    start_date: Annotated[datetime | None, Query()] = None,
    end_date: Annotated[datetime | None, Query()] = None,
):
    """Get statistical analysis for device measurements"""
    logger.info("get_device_stats: started", device_id=device_id)

    try:
        stats = await dao.get_device_stats(
            device_id=device_id,
            session=session,
            start_date=start_date,
            end_date=end_date,
        )
    except DeviceNotFoundException as e:
        logger.warning("get_device_stats: Device not found", device_id=device_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except MeasurementNotFoundException as e:
        logger.warning("get_device_stats: Measurement not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )

    logger.info("get_device_stats: completed")
    return stats


@router.post(
    "/api/v1/devices/{device_id}/users/",
    response_model=DeviceWithUsersSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_user_to_device(
    device_id: uuid.UUID,
    user_id: uuid.UUID,
    session: DbSession,
):
    """Add user to device (many-to-many relationship)"""
    logger.info("add_user_to_device: started", device_id=device_id)

    try:
        device = await dao.add_user_to_device(
            device_id=device_id,
            user_id=user_id,
            session=session,
        )
    except DeviceNotFoundException as e:
        logger.warning("add_user_to_device: Device not found", device_id=device_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except UserNotFoundException as e:
        logger.warning(
            "add_user_to_device: User not found",
            user_id=user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except UserAlreadyExistException as e:
        logger.warning(
            "add_user_to_device: User already exist",
            user_id=user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )

    logger.info("add_user_to_device: completed")
    return device


@router.get("/api/v1/devices/{device_id}/users/", response_model=list[FullUserSchema])
async def get_device_users(device_id: uuid.UUID, session: DbSession):
    """Get list of users assigned to device"""
    logger.info("get_device_users: started", device_id=device_id)

    try:
        device = await dao.get_device_users(
            session=session,
            device_id=device_id,
        )
    except DeviceNotFoundException as e:
        logger.warning("get_device_users: Device not found", device_id=device_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )

    logger.info("get_device_users: completed")
    return device
