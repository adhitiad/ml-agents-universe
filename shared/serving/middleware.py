"""FastAPI middleware untuk logging, error handling, dan CORS.

Module ini menyediakan:
- RequestLoggingMiddleware: Log setiap request dengan durasi
- ErrorHandlerMiddleware: Catch exceptions → ErrorResponse
- configure_cors: Setup CORS middleware

Typical usage:
    from shared.serving.middleware import (
        RequestLoggingMiddleware,
        ErrorHandlerMiddleware,
        configure_cors,
    )

    app = create_app()
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
    configure_cors(app, origins=["http://localhost:3000"])
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from shared.models.base import ErrorResponse


logger = logging.getLogger(__name__)


# ==========================================
# Request Logging Middleware
# ==========================================


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware untuk logging setiap HTTP request.

    Log format (JSON structured):
    - method, path, status_code, duration_ms
    - trace_id untuk request tracking
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request dan log hasilnya.

        Args:
            request: Incoming HTTP request.
            call_next: Handler berikutnya di middleware chain.

        Returns:
            HTTP Response.
        """
        trace_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # Inject trace_id ke request state
        request.state.trace_id = trace_id

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Tambahkan trace_id ke response headers
        response.headers["X-Trace-ID"] = trace_id

        logger.info(
            "HTTP %s %s → %d (%.1fms) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            trace_id,
        )

        return response


# ==========================================
# Error Handler Middleware
# ==========================================


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware untuk menangkap unhandled exceptions.

    Mengconvert exceptions menjadi ErrorResponse JSON yang
    konsisten, sehingga client selalu menerima format error
    yang sama.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request dan tangkap exceptions.

        Args:
            request: Incoming HTTP request.
            call_next: Handler berikutnya di middleware chain.

        Returns:
            HTTP Response (normal atau error).
        """
        try:
            return await call_next(request)
        except Exception as exc:
            trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))

            logger.exception(
                "Unhandled exception [%s]: %s",
                trace_id,
                str(exc),
            )

            error = ErrorResponse(
                status_code=500,
                error_type=type(exc).__name__,
                detail=str(exc),
                trace_id=trace_id,
            )

            return JSONResponse(
                content=error.model_dump(mode="json"),
                status_code=500,
            )


# ==========================================
# CORS Configuration
# ==========================================


def configure_cors(
    app: FastAPI,
    origins: list[str] | None = None,
    allow_credentials: bool = True,
    allow_methods: list[str] | None = None,
    allow_headers: list[str] | None = None,
) -> None:
    """Konfigurasi CORS middleware untuk FastAPI app.

    Args:
        app: FastAPI application instance.
        origins: Daftar allowed origins. Jangan gunakan wildcard "*" di production.
        allow_credentials: Izinkan credentials (cookies, auth headers).
        allow_methods: Allowed HTTP methods (None = ["GET", "POST", "PUT", "DELETE"]).
        allow_headers: Allowed headers (None = ["*"]).

    Raises:
        ValueError: Jika origins mengandung wildcard "*".
    """
    if origins and "*" in origins:
        logger.warning(
            "CORS wildcard origin '*' terdeteksi. "
            "Jangan gunakan di production — konfigurasi restrictively."
        )

    effective_origins = origins or ["http://localhost:3000"]
    effective_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "PATCH"]
    effective_headers = allow_headers or ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=effective_origins,
        allow_credentials=allow_credentials,
        allow_methods=effective_methods,
        allow_headers=effective_headers,
    )

    logger.info("CORS configured: origins=%s", effective_origins)
