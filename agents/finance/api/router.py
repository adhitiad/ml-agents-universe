"""Router for finance API."""

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from agents.finance.api.schemas import (
    AnalyzeRequest,
    PredictRequest,
    PredictResponse,
    StatusResponse,
)
from api.dependencies import rate_limiter
from shared.serving.websockets import manager


router = APIRouter(
    prefix="/v1/finance",
    tags=["finance"],
    dependencies=[Depends(rate_limiter)]
)

@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> Any:
    """Run prediction/execution for finance agent."""
    # Mocking agent call
    return PredictResponse(result=f"Processed: {request.input_data}")

@router.post("/analyze")
async def analyze(request: AnalyzeRequest) -> Any:
    """Run deeper analysis for finance agent."""
    return {"analysis": f"Analyzed {request.query}"}

@router.get("/status", response_model=StatusResponse)
async def status() -> Any:
    """Check health of the finance agent."""
    return StatusResponse()

@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """Real-time streaming interaction with finance agent."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Mock processing delay
            await asyncio.sleep(0.5)
            await manager.send_personal_message(f"[finance] Real-time response to: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
