"""
Detection routes: sync API for running detection (frontend).
"""
import io
import logging
from typing import Annotated

import requests
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from PIL import Image

from models.ollama_vlm import get_model, get_mock_detection_response
from schemas.detection import DetectionResponse
from services import minio_client
from utils.file_validation import MAX_IMAGE_UPLOAD_BYTES, is_image
from utils.pdf_extract import extract_text_from_pdf

logger = logging.getLogger(__name__)

detect_router = APIRouter(
    prefix="/detect",
    tags=["Detection"],
)


# -------------------------
# Synchronous detection (run VLM for frontend)
# -------------------------
def _load_spec_text_for_project(project_id: str) -> str:
    """Fetch design docs from MinIO for the project; extract text from PDFs and concatenate."""
    bucket = project_id
    try:
        object_names = minio_client.list_objects(bucket=bucket, prefix="designs/")
    except Exception:
        return ""
    parts = []
    for object_name in object_names:
        if not object_name.lower().endswith(".pdf"):
            continue
        try:
            data = minio_client.get_file(bucket=bucket, object_name=object_name)
            text = extract_text_from_pdf(data)
            if text.strip():
                parts.append(text.strip())
        except Exception:
            continue
    return "\n\n---\n\n".join(parts) if parts else ""


@detect_router.get("/prompt")
def get_inspection_prompt(project_id: str | None = None):
    """
    Return the full prompt (generic instructions + spec from project PDFs) that would be
    sent to the VLM for inspection. Use for display in the UI (e.g. "View prompt" popup).
    """
    spec_text = _load_spec_text_for_project(project_id) if project_id else ""
    model = get_model()
    prompt = model.get_prompt_for_spec(spec_text or None)
    return {"prompt": prompt}


@detect_router.post(
    "",
    response_model=DetectionResponse,
    responses={
        400: {"description": "No file uploaded, invalid content type, file too large, or invalid image content"},
        500: {"description": "Detection failed"},
    },
)
async def detect_fod(
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    project_id: Annotated[str | None, Form(description="Optional project ID for design-spec context")] = None,
):
    """
    Upload an image for synchronous detection. Returns analysis immediately.
    If project_id is provided, design spec PDFs for that project are read from storage
    and their content is used as the inspection specification for the VLM.
    """
    logger.info("POST detect_fod filename=%s project_id=%s", file.filename if file else None, project_id)
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_IMAGE_UPLOAD_BYTES // (1024 * 1024)} MB",
        )
    if not is_image(contents):
        raise HTTPException(status_code=400, detail="File content is not a valid PNG or JPEG image")

    try:
        image = Image.open(io.BytesIO(contents))
        if image.mode != "RGB":
            image = image.convert("RGB")
        max_size = 1024
        w, h = image.size
        if w > max_size or h > max_size:
            ratio = min(max_size / w, max_size / h)
            new_size = (int(w * ratio), int(h * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
    except Exception:
        logger.exception("Could not process image")
        raise HTTPException(status_code=400, detail="Could not process image")

    spec_text = _load_spec_text_for_project(project_id) if project_id else ""

    model = get_model()
    try:
        result = model.detect_fod(image, None, spec_text or None)
        logger.info("Detection complete filename=%s pass_fail=%s", file.filename, result.pass_fail)
        return result
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        logger.warning("Detection skipped (Ollama unreachable) — returning mock response filename=%s", file.filename)
        return get_mock_detection_response()
    except Exception:
        logger.exception("Detection failed filename=%s", file.filename)
        raise HTTPException(status_code=500, detail="Detection failed")