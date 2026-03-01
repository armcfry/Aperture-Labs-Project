"""
Pydantic Schemas for FOD Detection API
"""

from pydantic import BaseModel


class DetectionResponse(BaseModel):
    response: str
    model: str
    inference_time_ms: float
