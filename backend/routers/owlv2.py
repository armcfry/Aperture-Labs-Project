import io

from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from PIL import Image

from models.owlv2 import get_detector


router = APIRouter(
    prefix="/owlv2",
    tags=["OWLv2 Detection"],
)


@router.post(
    "/detect",
    response_class=StreamingResponse,
    responses={200: {"content": {"image/png": {}}}},
)
async def detect_objects(
    file: UploadFile = File(...),
    queries: str = Query(
        default="foreign object, debris, defect, anomaly",
        description="Comma-separated list of objects to detect",
    ),
    confidence: float = Query(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold (0-1)",
    ),
):
    """
    Detect objects in an image using OWLv2 and return the image with bounding boxes drawn.

    - **file**: Image file (PNG, JPEG)
    - **queries**: Comma-separated text queries for objects to detect
    - **confidence**: Minimum confidence threshold for detections
    """
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    text_queries = [q.strip() for q in queries.split(",") if q.strip()]

    detector = get_detector()
    annotated_bytes = detector.detect_and_draw_bytes(
        image=image,
        text_queries=text_queries,
        confidence_threshold=confidence,
        output_format="PNG",
    )

    return StreamingResponse(
        io.BytesIO(annotated_bytes),
        media_type="image/png",
    )
