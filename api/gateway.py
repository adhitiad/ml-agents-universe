"""Unified API Gateway untuk ML Agents Universe."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.limiter import limiter
from api.routes.chat import router as unified_chat_router
from api.routes.omnichannel import router as omnichannel_router
from api.routes.ws_chat import router as ws_chat_router
from shared.models.base import ErrorResponse
from shared.monitoring.metrics import request_count
from shared.serving.model_cache import model_cache


# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api.gateway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Model Warmup
    logger.info("Starting ML Agents Universe API Gateway...")
    model_cache.load_all_models()
    yield
    # Shutdown
    logger.info("Shutting down API Gateway...")


# Buat instance FastAPI
app = FastAPI(
    title="ML Agents Universe API Gateway",
    description="Unified API Gateway untuk seluruh domain agen cerdas.",
    version="1.0.0",
    lifespan=lifespan,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        429: {"model": ErrorResponse, "description": "Too Many Requests"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)

# Registrasi Limiter (Heat Optimization)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Konfigurasi CORS (Restrictive)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://ml-agents.local"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount Unified Chat & Omnichannel Routers
app.include_router(unified_chat_router)
app.include_router(ws_chat_router)
app.include_router(omnichannel_router)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    request_count.labels(domain="gateway", status="health_check").inc()
    return {"status": "ok", "services": "all"}
