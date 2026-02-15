"""
Pydantic Schemas for FOD Detection API
"""

from pydantic import BaseModel


class DetectionResponse(BaseModel):
    response: str
