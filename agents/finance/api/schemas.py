"""Schemas for finance API."""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    input_data: str = Field(..., description="Data input for finance prediction.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"input_data": "sample finance request"}
            ]
        }
    }

class PredictResponse(BaseModel):
    result: str = Field(..., description="Prediction result.")
    agent: str = Field(default="finance")

class AnalyzeRequest(BaseModel):
    query: str = Field(..., description="Analysis query.")

class StatusResponse(BaseModel):
    status: str = Field(default="healthy")
    agent: str = Field(default="finance")
