"""FastAPI application factory dan health check endpoint.

Module ini menyediakan:
- create_app: Factory function untuk membuat FastAPI instance
- add_health_check: Register /health endpoint

Typical usage:
    from shared.serving.app import create_app
    from shared.env.settings import APISettings

    settings = APISettings()
    app = create_app(title="ML Agents API", version="0.1.0")
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from shared.models.base import (
    ComponentHealth,
    HealthStatus,
    HealthStatusEnum,
)


logger = logging.getLogger(__name__)

# Waktu aplikasi di-start (untuk uptime calculation)
_app_start_time: float = 0.0


@asynccontextmanager
async def _default_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Default lifespan handler — track app start time."""
    global _app_start_time
    _app_start_time = time.time()
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")


def create_app(
    title: str = "ML Agents Universe API",
    version: str = "0.1.0",
    description: str = "Multi-domain AI Agent Orchestration API",
    lifespan: Any | None = None,
    debug: bool = False,
) -> FastAPI:
    """Factory function untuk membuat FastAPI application.

    Membuat instance FastAPI dengan konfigurasi standar:
    - Title, version, description
    - Lifespan handler
    - Default health check endpoint

    Args:
        title: Judul API.
        version: Versi API.
        description: Deskripsi API.
        lifespan: Custom lifespan context manager (None = default).
        debug: Mode debug aktif/nonaktif.

    Returns:
        FastAPI application instance.
    """
    app = FastAPI(
        title=title,
        version=version,
        description=description,
        lifespan=lifespan or _default_lifespan,
        debug=debug,
    )

    # Register default health check
    add_health_check(app)

    logger.info("FastAPI app created: %s v%s", title, version)
    return app


def add_health_check(
    app: FastAPI,
    path: str = "/health",
    checks: list[Callable[[], ComponentHealth]] | None = None,
) -> None:
    """Register health check endpoint.

    Endpoint mengembalikan aggregated health status dari
    semua komponen yang di-register.

    Args:
        app: FastAPI application instance.
        path: Path untuk health check endpoint.
        checks: Daftar callable yang mengembalikan ComponentHealth.
    """
    health_checks: list[Callable[[], ComponentHealth]] = checks or []

    @app.get(
        path,
        response_model=HealthStatus,
        tags=["health"],
        summary="Health Check",
        description="Cek status kesehatan service dan semua komponen.",
    )
    async def health_check() -> JSONResponse:
        """Health check endpoint."""
        component_results: list[ComponentHealth] = []

        for check_fn in health_checks:
            try:
                result = check_fn()
                component_results.append(result)
            except Exception as exc:
                component_results.append(
                    ComponentHealth(
                        name=check_fn.__name__,
                        status=HealthStatusEnum.UNHEALTHY,
                        message=str(exc),
                    )
                )

        # Determine overall status
        if any(c.status == HealthStatusEnum.UNHEALTHY for c in component_results):
            overall = HealthStatusEnum.UNHEALTHY
        elif any(c.status == HealthStatusEnum.DEGRADED for c in component_results):
            overall = HealthStatusEnum.DEGRADED
        else:
            overall = HealthStatusEnum.HEALTHY

        uptime = time.time() - _app_start_time if _app_start_time > 0 else 0.0

        status = HealthStatus(
            status=overall,
            version=app.version,
            uptime_seconds=uptime,
            checks=component_results,
        )

        http_status = 200 if overall == HealthStatusEnum.HEALTHY else 503
        return JSONResponse(
            content=status.model_dump(mode="json"),
            status_code=http_status,
        )

    logger.debug("Health check endpoint registered: %s", path)
