"""API serving utilities dan middleware.

Module ini menyediakan:
- create_app: FastAPI application factory
- add_health_check: Register /health endpoint
- RequestLoggingMiddleware: HTTP request logging
- ErrorHandlerMiddleware: Exception → ErrorResponse
- configure_cors: CORS middleware setup
"""

from shared.serving.app import add_health_check, create_app
from shared.serving.middleware import (
    ErrorHandlerMiddleware,
    RequestLoggingMiddleware,
    configure_cors,
)


__all__: list[str] = [
    "ErrorHandlerMiddleware",
    "RequestLoggingMiddleware",
    "add_health_check",
    "configure_cors",
    "create_app",
]
