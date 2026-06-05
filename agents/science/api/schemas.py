"""Schemas for science API."""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    input_data: str = Field(..., description="Data input for science prediction.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"input_data": "sample science request"}
            ]
        }
    }

class PredictResponse(BaseModel):
    result: str = Field(..., description="Prediction result.")
    agent: str = Field(default="science")

class AnalyzeRequest(BaseModel):
    query: str = Field(..., description="Analysis query.")

class StatusResponse(BaseModel):
    status: str = Field(default="healthy")
    agent: str = Field(default="science")
