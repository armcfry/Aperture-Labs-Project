"""
Pydantic Schemas for FOD Detection API
"""

from pydantic import BaseModel


class DefectLocation(BaseModel):
    x: float  # 0-100, percentage from left
    y: float  # 0-100, percentage from top


class DefectSchema(BaseModel):
    id: str
    location: DefectLocation
    severity: str  # "critical" | "major" | "minor"
    description: str


class DetectionResponse(BaseModel):
    response: str
    model: str
    inference_time_ms: float
    pass_fail: str  # "pass" | "fail"
    defects: list[DefectSchema] | None = None  # parsed from response when possible
