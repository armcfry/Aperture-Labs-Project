"""
Pydantic Schemas for FOD Detection API
"""

from pydantic import BaseModel
from typing import Optional


class DetectionResponse(BaseModel):
    response: str
    model: Optional[str] = None
    inference_time_ms: Optional[float] = None
