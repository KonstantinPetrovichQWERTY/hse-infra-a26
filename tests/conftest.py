from collections.abc import AsyncGenerator, Generator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import create_app
from src.core.dependencies import get_db


async def fake_db() -> AsyncGenerator[AsyncSession, None]:
    yield cast(AsyncSession, None)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app = create_app(init_db=False)
    app.dependency_overrides[get_db] = fake_db
    with TestClient(app) as test_client:
        yield test_client
