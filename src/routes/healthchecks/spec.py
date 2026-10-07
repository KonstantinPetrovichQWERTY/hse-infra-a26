from enum import Enum


class API(str, Enum):
    """Enumeration of health check endpoint paths."""

    LIVENESS = "/health"
    READINESS = "/readness"
