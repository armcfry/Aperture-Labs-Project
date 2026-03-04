"""
Synchronous FOD detection endpoint for frontend.
Uses Ollama VLM for immediate detection results.
When Ollama is unavailable (not running, timeout), returns mock/demo result so the UI still shows a result.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import requests

from models.ollama_vlm import get_model, get_mock_detection_response
from schemas.detection import DetectionResponse


router = APIRouter(
    prefix="/detect",
    tags=["Detection"],
)


@router.post("", response_model=DetectionResponse)
async def detect_fod(file: UploadFile = File(...)):
    """Upload an image for synchronous FOD detection. Returns analysis immediately."""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        if image.mode != "RGB":
            image = image.convert("RGB")
        # Resize large images to avoid Ollama 500 (vision models have resolution limits)
        max_size = 1024
        w, h = image.size
        if w > max_size or h > max_size:
            ratio = min(max_size / w, max_size / h)
            new_size = (int(w * ratio), int(h * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process image: {str(e)}")

    model = get_model()
    try:
        return model.detect_fod(image)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        # Ollama not running or timed out: return mock result so frontend shows a result
        return get_mock_detection_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
