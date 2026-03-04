"""
Ollama-based VLM for FOD Detection
Uses Qwen2.5-VL by default (ollama pull qwen2.5vl or qwen2.5vl:7b).
"""

import base64
import io
import os
import re
import time
from typing import Optional
import requests
from PIL import Image

from schemas.detection import DetectionResponse, DefectSchema, DefectLocation

# Default: Qwen2.5-VL 7B. Override with env OLLAMA_VLM_MODEL (e.g. qwen2.5vl:72b).
DEFAULT_MODEL = os.environ.get("OLLAMA_VLM_MODEL", "qwen2.5vl:7b")

# Default positions when the model doesn't provide (x%, y%)
_DEFAULT_POSITIONS: list[tuple[float, float]] = [
    (25, 30), (50, 50), (75, 35), (35, 70), (65, 65),
]


def _parse_pass_fail(response: str) -> str:
    """Extract pass/fail from response. Expects 'RESULT: PASS' or 'RESULT: FAIL'."""
    lower = response.lower().strip()
    if "result: pass" in lower or "result:pass" in lower:
        return "pass"
    if "result: fail" in lower or "result:fail" in lower:
        return "fail"
    # Out-of-scope / wrong context → fail
    if any(p in lower for p in ("out of scope", "does not show", "not show a runway", "not an inspection area", "unrelated to", "wrong context")):
        return "fail"
    # Fallback: infer from content
    if any(p in lower for p in ("no fod", "no foreign object", "no debris", "clear", "no visible defect")):
        return "pass"
    if any(p in lower for p in ("fod", "foreign object", "debris", "defect", "anomaly")):
        return "fail"
    return "fail"


def _parse_defects_from_response(response: str) -> list[DefectSchema]:
    """Parse VLM response into defects; extract (x%, y%) when present."""
    # Build mutable entries so we can append Location/Action to description
    entries: list[dict] = []
    lines = response.splitlines()
    current_severity: Optional[str] = None
    defect_index = 0
    coord_re = re.compile(r"\((\d+(?:\.\d+)?)\s*%?\s*,\s*(\d+(?:\.\d+)?)\s*%?\)")

    for i, line in enumerate(lines):
        lower = line.lower()
        if "critical" in lower and ("failure" in lower or ":" in lower):
            current_severity = "critical"
        elif "major" in lower and ("issue" in lower or ":" in lower):
            current_severity = "major"
        elif "minor" in lower and ("issue" in lower or ":" in lower):
            current_severity = "minor"

        if entries and (lower.strip().startswith("location:") or lower.strip().startswith("recommended action:")):
            extra = re.sub(r"^[\s\S]*?:\s*", "", line, flags=re.I).strip()
            if extra:
                entries[-1]["description"] += f" — {extra}"
            continue

        bullet_match = re.match(r"^[\s]*[•\-*]\s*(.+)", line)
        if bullet_match and current_severity:
            rest = bullet_match[1].strip()
            if len(rest) < 5:
                continue
            coord_match = coord_re.search(rest)
            if coord_match:
                x = max(0, min(100, float(coord_match.group(1))))
                y = max(0, min(100, float(coord_match.group(2))))
                desc = coord_re.sub("", rest).strip().strip("— -") or rest
            else:
                idx = defect_index % len(_DEFAULT_POSITIONS)
                x, y = _DEFAULT_POSITIONS[idx]
                desc = rest

            entries.append({
                "id": f"DEF-{str(defect_index + 1).zfill(3)}",
                "x": x, "y": y,
                "severity": current_severity,
                "description": desc,
            })
            defect_index += 1

    defects = [
        DefectSchema(
            id=e["id"],
            location=DefectLocation(x=e["x"], y=e["y"]),
            severity=e["severity"],
            description=e["description"],
        )
        for e in entries
    ]

    if not defects and re.search(r"\b(fod|foreign object|debris|defect|anomal)\b", response, re.I):
        snippet = response[:200].replace("\n", " ").strip()
        defects.append(
            DefectSchema(
                id="DEF-001",
                location=DefectLocation(x=50, y=50),
                severity="critical" if "critical" in response.lower() else "major",
                description=snippet or "Anomaly detected (see full analysis below)",
            )
        )
    return defects


def get_mock_detection_response() -> DetectionResponse:
    """Return a mock detection result when Ollama is unavailable (e.g. not running or timeout)."""
    mock_text = """INSPECTION SUMMARY (Demo - AI service unavailable)

Ollama was not reachable. For real detection use Qwen2.5-VL: run `ollama serve` and `ollama pull qwen2.5vl:7b` (or `ollama pull qwen2.5vl`).

Specification: Design specs
Images Analyzed: 1
Defects Detected: 2 anomalies found
Status: FAIL - Defects present

CRITICAL FAILURES:
• Surface Integrity: Foreign object detected (25%, 30%)
  - Location: Upper-left quadrant
  - Recommended Action: Reject and rework

MAJOR ISSUES:
• Debris detected at center region (50%, 50%)
  - Recommended Action: Quality review required

RECOMMENDATION: Product does not meet manufacturing specifications. Immediate rework required.
RESULT: FAIL"""
    defects = _parse_defects_from_response(mock_text)
    return DetectionResponse(
        response=mock_text,
        model="mock (Ollama/Qwen2.5-VL unavailable)",
        inference_time_ms=0,
        pass_fail="fail",
        defects=defects,
    )


class OllamaVLM:
    def __init__(
        self,
        model_name: Optional[str] = None,
        ollama_host: str = "http://localhost:11434"
    ):
        self.model_name = model_name if model_name is not None else DEFAULT_MODEL
        self.ollama_host = ollama_host
        self.is_loaded = False

    def load_model(self) -> bool:
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            if response.status_code == 200:
                self.is_loaded = True
                return True
            return False
        except requests.exceptions.ConnectionError:
            return False

    def detect_fod(self, image: Image.Image, prompt: Optional[str] = None) -> DetectionResponse:
        """
        Analyze an image for Foreign Object Debris using the configured VLM.

        Args:
            image: PIL Image to analyze to be converted to base64 PNG.
            prompt: Custom prompt for the VLM. If None, uses default FOD detection prompt.

        Returns:
            DetectionResponse containing the model's response, model name, and inference time.
        """
        if not self.is_loaded:
            self.load_model()

        if prompt is None:
            prompt = (
                "You are inspecting this image for Foreign Object Debris (FOD) as part of a quality inspection. "
                "The inspection context is: airport runways, tarmac, or aircraft maintenance areas.\n\n"
                "1) First, determine whether this image shows the correct inspection context (runway, tarmac, aircraft surface, or similar). "
                "If the image clearly does NOT show such a scene (e.g. random illustration, artwork, text/graphics, landmarks, unrelated photos), "
                "then respond with a brief explanation and end with: RESULT: FAIL. "
                "Example: 'This image does not show a runway or aircraft inspection area. It appears to be [description]. Image is out of scope for FOD inspection.' RESULT: FAIL\n\n"
                "2) Only if the image DOES show an appropriate inspection area, then check for FOD:\n"
                "   - If you find NO FOD: explain why it passes (e.g. 'No foreign object debris detected. The surface appears clear.'). End with: RESULT: PASS\n"
                "   - If you find FOD: list each defect with severity (CRITICAL FAILURES, MAJOR ISSUES, or MINOR ISSUES) and approximate position (X%, Y%). End with: RESULT: FAIL\n"
                "3) You must end your response with exactly one line: RESULT: PASS or RESULT: FAIL.\n\n"
                "Do not respond with only 'RESULT: PASS' or 'RESULT: FAIL'. Always include the description and the reason."
            )

        image_base64 = self._image_to_base64(image)

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        }

        start_time = time.time()

        response = requests.post(
            f"{self.ollama_host}/api/generate",
            json=payload,
            timeout=120
        )

        inference_time = (time.time() - start_time) * 1000

        if response.status_code == 200:
            raw_response = response.json().get("response", "")
            print(raw_response)
            pass_fail = _parse_pass_fail(raw_response)
            defects = _parse_defects_from_response(raw_response)
            if pass_fail == "fail" and not defects:
                defects = [
                    DefectSchema(
                        id="DEF-001",
                        location=DefectLocation(x=50, y=50),
                        severity="major",
                        description="Inspection failed. See full analysis above for details.",
                    )
                ]
            return DetectionResponse(
                response=raw_response,
                model=self.model_name,
                inference_time_ms=inference_time,
                pass_fail=pass_fail,
                defects=defects if defects else None,
            )
        else:
            error = f"Error: {response.status_code}"
            return DetectionResponse(
                response=error,
                model=self.model_name,
                inference_time_ms=inference_time,
                pass_fail="fail",
                defects=[
                    DefectSchema(
                        id="DEF-001",
                        location=DefectLocation(x=50, y=50),
                        severity="major",
                        description=error + ". Detection request failed.",
                    )
                ],
            )

    def _image_to_base64(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


# Singleton ensures that there's only one instance of OllmaVLM. Used by get_model()
_instances: dict[str, OllamaVLM] = {}

def get_model(model_name: Optional[str] = None) -> OllamaVLM:
    name = model_name if model_name is not None else DEFAULT_MODEL
    if name not in _instances:
        _instances[name] = OllamaVLM(model_name=name)
    return _instances[name]
