"""
Pydantic Schemas for FOD Detection API
"""

from pydantic import BaseModel
from typing import Optional, List


class DetectionResponse(BaseModel):
    response: str
    model: str
    inference_time_ms: float
    model: Optional[str] = None
    inference_time_ms: Optional[float] = None

class BoundingBox(BaseModel):
    label: str
    box: List[int]
    score: float