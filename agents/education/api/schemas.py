"""Schemas for education API."""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    input_data: str = Field(..., description="Data input for education prediction.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"input_data": "sample education request"}
            ]
        }
    }

class PredictResponse(BaseModel):
    result: str = Field(..., description="Prediction result.")
    agent: str = Field(default="education")

class AnalyzeRequest(BaseModel):
    query: str = Field(..., description="Analysis query.")

class StatusResponse(BaseModel):
    status: str = Field(default="healthy")
    agent: str = Field(default="education")
