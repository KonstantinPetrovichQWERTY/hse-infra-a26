from http import HTTPStatus

from fastapi import APIRouter
from sqlalchemy import select

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import SQLAlchemyError
import structlog

from src.routes.healthchecks.schema import HealthCheckReadinessOutScheme
from src.routes.healthchecks.spec import API
from src.settings import settings

router = APIRouter(tags=["health-checks"])
logger = structlog.get_logger()


@router.get(API.LIVENESS, status_code=HTTPStatus.OK)
async def liveness() -> dict:
    """Basic service liveness check endpoint.

    Provides immediate feedback about service availability.

    Returns:
        dict: Simple status response
    """
    logger.info("liveness checked")
    return {"status": "OK", "message": "Service is alive"}


@router.get(
    API.READINESS,
    status_code=HTTPStatus.OK,
    response_model=HealthCheckReadinessOutScheme,
)
async def readiness():
    """Comprehensive service readiness check endpoint.

    Verifies essential service dependencies including:
    - Database connectivity

    Returns:
        HealthCheckReadinessOutScheme: Detailed status report containing:
            - items: List of checked services with their statuses

    Notes:
        Creates a new database connection pool for each check to verify
        actual connection capability
    """
    logger.info("readiness: started")

    items = []
    msg = ""

    is_alive_database = False
    try:
        engine = create_async_engine(url=str(settings.DB_URI))

        async with engine.connect() as connect:
            await connect.execute(select(1))

        msg = "Stable connection to database"
        is_alive_database = True

    except SQLAlchemyError as e:
        logger.warning("readiness: SQLAlchemyError", err=e)
        msg = f"Database connection error: {str(e)}"
    except ConnectionError as e:
        logger.warning("readiness: ConnectionError", err=e)
        msg = "No connection to database"
    except Exception as e:
        logger.warning("readiness: Unexpected error", err=e)
        msg = f"Unexpected error: {str(e)}"

    finally:
        items.append({"service": "database", "is_alive": is_alive_database, "msg": msg})

    response = {"items": items}
    logger.info("readiness: completed", items=items)
    return response
