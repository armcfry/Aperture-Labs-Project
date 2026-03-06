"""
Pydantic Schemas for FOD Detection API
"""

from pydantic import BaseModel


class DefectSchema(BaseModel):
    id: str
    severity: str  # "critical" | "major" | "minor"
    description: str


class DetectionResponse(BaseModel):
    response: str
    model: str
    inference_time_ms: float
    pass_fail: str  # "pass" | "fail"
    defects: list[DefectSchema] | None = None  # parsed from response when possible
    prompt_used: str | None = None  # full prompt (generic + spec) sent to the VLM, for display
