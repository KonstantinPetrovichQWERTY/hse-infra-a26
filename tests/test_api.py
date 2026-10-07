from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from src.core.utils import __version__
from src.routes.devices import views as device_views
from src.routes.devices.exceptions import (
    DeviceNotFoundException,
    DeviceSerialNumberException,
)
from src.routes.devices.schemas import (
    DeviceSchema,
    DeviceStatsResponse,
    MeasurementSchema,
    StatsValues,
)
from src.routes.users import views as user_views
from src.routes.users.exceptions import UserAlreadyExistException
from src.routes.users.schemas import FullUserSchema


def test_health_and_version(client: TestClient) -> None:
    health_response = client.get("/health")
    version_response = client.get("/version")

    assert health_response.status_code == 200
    assert health_response.json() == {
        "status": "OK",
        "message": "Service is alive",
    }
    assert version_response.status_code == 200
    assert version_response.json() == {"version": __version__}


def test_create_user_returns_201(client: TestClient, monkeypatch) -> None:
    user_id = uuid4()

    async def create_user(*, session, user_data):
        return FullUserSchema(id=user_id, name=user_data.name)

    monkeypatch.setattr(user_views.dao, "create_user", create_user)

    response = client.post("/api/v1/users/", json={"name": "Alice"})

    assert response.status_code == 201
    assert response.json() == {"id": str(user_id), "name": "Alice"}


def test_create_user_duplicate_returns_400(client: TestClient, monkeypatch) -> None:
    async def create_user(*, session, user_data):
        raise UserAlreadyExistException()

    monkeypatch.setattr(user_views.dao, "create_user", create_user)

    response = client.post("/api/v1/users/", json={"name": "Alice"})

    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}


def test_register_device_returns_201(client: TestClient, monkeypatch) -> None:
    device_id = uuid4()

    async def register_new_device(*, session, device_data):
        return DeviceSchema(id=device_id, serial_number=device_data.serial_number)

    monkeypatch.setattr(device_views.dao, "register_new_device", register_new_device)

    response = client.post(
        "/api/v1/devices/register_new_device/",
        json={"serial_number": "SN-001"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": str(device_id),
        "serial_number": "SN-001",
    }


def test_register_device_duplicate_returns_400(client: TestClient, monkeypatch) -> None:
    async def register_new_device(*, session, device_data):
        raise DeviceSerialNumberException()

    monkeypatch.setattr(device_views.dao, "register_new_device", register_new_device)

    response = client.post(
        "/api/v1/devices/register_new_device/",
        json={"serial_number": "SN-001"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Device with this serial number already exists"
    }


def test_device_validation_rejects_short_serial_number(client: TestClient) -> None:
    response = client.post(
        "/api/v1/devices/register_new_device/",
        json={"serial_number": "x"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "serial_number"]


def test_get_device_not_found_returns_404(client: TestClient, monkeypatch) -> None:
    async def get_device(*, session, device_id):
        raise DeviceNotFoundException()

    monkeypatch.setattr(device_views.dao, "get_device", get_device)

    response = client.get(f"/api/v1/devices/{uuid4()}/")

    assert response.status_code == 404
    assert response.json() == {"detail": "Coil not found"}


def test_add_measurement_returns_measurement(client: TestClient, monkeypatch) -> None:
    device_id = uuid4()
    measurement_id = uuid4()
    timestamp = datetime.now(UTC).replace(microsecond=0)

    async def add_measurement(*, session, device_id, measurement_data):
        return MeasurementSchema(
            id=measurement_id,
            device_id=device_id,
            timestamp=timestamp,
            **measurement_data.model_dump(),
        )

    monkeypatch.setattr(device_views.dao, "add_measurement", add_measurement)

    response = client.post(
        f"/api/v1/devices/{device_id}/measurements/",
        json={"x": 1.0, "y": -2.5, "z": 3},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": str(measurement_id),
        "device_id": str(device_id),
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "x": 1.0,
        "y": -2.5,
        "z": 3.0,
    }


def test_stats_response_is_serialized(client: TestClient, monkeypatch) -> None:
    device_id = uuid4()
    stats = DeviceStatsResponse(
        device_id=device_id,
        x=StatsValues(min=1, max=3, count=2, sum=4, median=2),
        y=StatsValues(min=0, max=4, count=2, sum=4, median=2),
        z=StatsValues(min=-1, max=1, count=2, sum=0, median=0),
        period={"start": None, "end": None},
    )

    async def get_device_stats(*, session, device_id, start_date, end_date):
        return stats

    monkeypatch.setattr(device_views.dao, "get_device_stats", get_device_stats)

    response = client.get(f"/api/v1/devices/{device_id}/stats/")

    assert response.status_code == 200
    assert response.json()["x"] == {
        "min": 1.0,
        "max": 3.0,
        "count": 2,
        "sum": 4.0,
        "median": 2.0,
    }
