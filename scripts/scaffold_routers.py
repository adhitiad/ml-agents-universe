from pathlib import Path


base = Path("e:/dev/ml-agents-universe")
domains = [
    "nlp",
    "finance",
    "economy",
    "education",
    "entertainment",
    "mathematics",
    "science",
]

schema_template = '''"""Schemas for {domain} API."""

from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    input_data: str = Field(..., description="Data input for {domain} prediction.")

    model_config = {{
        "json_schema_extra": {{
            "examples": [
                {{"input_data": "sample {domain} request"}}
            ]
        }}
    }}

class PredictResponse(BaseModel):
    result: str = Field(..., description="Prediction result.")
    agent: str = Field(default="{domain}")
    
class AnalyzeRequest(BaseModel):
    query: str = Field(..., description="Analysis query.")

class StatusResponse(BaseModel):
    status: str = Field(default="healthy")
    agent: str = Field(default="{domain}")
'''

router_template = '''"""Router for {domain} API."""

import asyncio
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from typing import Any

from agents.{domain}.api.schemas import PredictRequest, PredictResponse, AnalyzeRequest, StatusResponse
from api.dependencies import rate_limiter
from shared.serving.websockets import manager

router = APIRouter(
    prefix="/v1/{domain}",
    tags=["{domain}"],
    dependencies=[Depends(rate_limiter)]
)

@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> Any:
    """Run prediction/execution for {domain} agent."""
    # Mocking agent call
    return PredictResponse(result=f"Processed: {{request.input_data}}")

@router.post("/analyze")
async def analyze(request: AnalyzeRequest) -> Any:
    """Run deeper analysis for {domain} agent."""
    return {{"analysis": f"Analyzed {{request.query}}"}}

@router.get("/status", response_model=StatusResponse)
async def status() -> Any:
    """Check health of the {domain} agent."""
    return StatusResponse()

@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """Real-time streaming interaction with {domain} agent."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Mock processing delay
            await asyncio.sleep(0.5)
            await manager.send_personal_message(f"[{domain}] Real-time response to: {{data}}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
'''

for d in domains:
    schemas_path = base / f"agents/{d}/api/schemas.py"
    router_path = base / f"agents/{d}/api/router.py"

    schemas_path.write_text(schema_template.format(domain=d))
    router_path.write_text(router_template.format(domain=d))

print("Routers and schemas scaffolded.")
