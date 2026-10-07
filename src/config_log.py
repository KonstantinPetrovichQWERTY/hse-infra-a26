import logging

import structlog


def configure_logging():
    """Configures structured logging for the application using structlog.

    Sets up:
    - Structured log formatting with key-value pairs
    - Console-based log output
    - ISO 8601 timestamps
    - Log level filtering
    - Exception stack trace capturing
    - Integration with standard logging module
    - Format logs as structured JSON-like records
    - Use INFO level by default
    """
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler()],
    )
