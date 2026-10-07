from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config_log import configure_logging
from src.middleware.log_middleware import logging_middleware
from src.utils import get_service_name
from src.version import __version__
from src.settings import settings
from src.routes.healthchecks.views import router as health_router
from src.routes.devices.views import router as devices_router
from src.routes.users.views import router as users_router
from src.database.database import sessionmanager


def create_app(init_db: bool = True) -> FastAPI:
    """Factory function for creating and configuring the FastAPI application.

    Initializes core application components including:
    - Database connection management
    - Middleware (CORS, logging)
    - API routes

    Args:
        init_db (bool): Whether to initialize database connections.
            Defaults to True. Set to False for testing scenarios.

    Returns:
        FastAPI: Configured application instance.
    """
    if init_db:
        sessionmanager.init(str(settings.DB_URI))

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    app = FastAPI(
        title=get_service_name(),
        version=__version__,
        middleware=[],
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    configure_logging()
    app.middleware("http")(logging_middleware)

    app.include_router(users_router)
    app.include_router(devices_router)
    app.include_router(health_router)

    return app
