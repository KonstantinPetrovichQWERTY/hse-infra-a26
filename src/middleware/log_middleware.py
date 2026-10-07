import time
from collections.abc import Callable

import structlog
from fastapi import Request

logger = structlog.get_logger(__name__)


async def logging_middleware(request: Request, call_next: Callable):
    """FastAPI middleware for request logging with performance metrics.

    Logs:
    - Request start with metadata (method, URL, headers, query params)
    - Request completion with status code and processing time
    - Request failures with error details

    Args:
        request: Incoming FastAPI request object
        call_next: Next middleware/handler in the processing chain

    Returns:
        response: Generated HTTP response

    Raises:
        Exception: Propagates any exceptions from downstream handlers
    """
    start_time = time.time()

    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
        query_params=dict(request.query_params),
    )

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(
            "Request failed",
            method=request.method,
            url=str(request.url),
            error=str(e),
        )
        raise

    process_time = (time.time() - start_time) * 1000
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=f"{process_time:.2f}ms",
    )

    return response
