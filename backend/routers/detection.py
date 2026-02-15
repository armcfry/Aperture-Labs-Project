"""
Detection Router
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io

from models.qwen_vlm import get_model
from schemas.detection import DetectionResponse


router = APIRouter(prefix="/api", tags=["detection"])


@router.post("/detect", response_model=DetectionResponse)
async def detect_fod(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        if image.mode != "RGB":
            image = image.convert("RGB")
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Could not process image: {str(error)}")

    model = get_model()

    try:
        raw_response = model.detect_fod(image)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(error)}")

    return DetectionResponse(response=raw_response)
