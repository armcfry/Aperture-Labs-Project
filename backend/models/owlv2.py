"""
OWLv2-based object detection for FOD Detection with bounding boxes.
"""

import io
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

import torch
from transformers import Owlv2Processor, Owlv2ForObjectDetection


class OWLv2Detector:
    def __init__(
        self,
        model_name: str = "google/owlv2-base-patch16-ensemble",
        device: Optional[str] = None,
    ):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = None
        self.model = None
        self.is_loaded = False

    def load_model(self) -> bool:
        """Load the OWLv2 model and processor."""
        if self.is_loaded:
            return True
        try:
            self.processor = Owlv2Processor.from_pretrained(self.model_name)
            self.model = Owlv2ForObjectDetection.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            return True
        except Exception as e:
            print(f"[OWLv2] Failed to load model: {e}")
            return False

    def detect_and_draw(
        self,
        image: Image.Image,
        text_queries: list[str],
        confidence_threshold: float = 0.1,
        box_color: str = "red",
        box_width: int = 3,
    ) -> Image.Image:
        """
        Detect objects and draw bounding boxes on the image.

        Args:
            image: PIL Image to analyze.
            text_queries: List of text descriptions to detect (e.g., ["foreign object", "debris", "defect"]).
            confidence_threshold: Minimum confidence score to draw a box (0-1).
            box_color: Color for bounding boxes.
            box_width: Line width for bounding boxes.

        Returns:
            PIL Image with bounding boxes drawn.
        """
        if not self.is_loaded:
            self.load_model()

        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Process inputs
        inputs = self.processor(
            text=[text_queries],
            images=image,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Post-process results
        target_sizes = torch.tensor([image.size[::-1]], device=self.device)
        results = self.processor.post_process_object_detection(
            outputs=outputs,
            target_sizes=target_sizes,
            threshold=confidence_threshold,
        )[0]

        # Draw bounding boxes on a copy of the image
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)

        # Try to load a font, fall back to default
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except (OSError, IOError):
            font = ImageFont.load_default()

        boxes = results["boxes"].cpu().numpy()
        scores = results["scores"].cpu().numpy()
        labels = results["labels"].cpu().numpy()

        for box, score, label_idx in zip(boxes, scores, labels):
            x1, y1, x2, y2 = box.astype(int)
            label_text = text_queries[label_idx] if label_idx < len(text_queries) else "object"

            # Draw rectangle
            draw.rectangle([x1, y1, x2, y2], outline=box_color, width=box_width)

            # Draw label with confidence
            label_str = f"{label_text}: {score:.2f}"
            text_bbox = draw.textbbox((x1, y1), label_str, font=font)
            text_bg = [text_bbox[0] - 2, text_bbox[1] - 2, text_bbox[2] + 2, text_bbox[3] + 2]
            draw.rectangle(text_bg, fill=box_color)
            draw.text((x1, y1), label_str, fill="white", font=font)

        return annotated_image

    def detect_and_draw_bytes(
        self,
        image: Image.Image,
        text_queries: list[str],
        confidence_threshold: float = 0.1,
        output_format: str = "PNG",
    ) -> bytes:
        """
        Detect objects and return annotated image as bytes.

        Args:
            image: PIL Image to analyze.
            text_queries: List of text descriptions to detect.
            confidence_threshold: Minimum confidence score (0-1).
            output_format: Image format (PNG, JPEG).

        Returns:
            Annotated image as bytes.
        """
        annotated = self.detect_and_draw(
            image=image,
            text_queries=text_queries,
            confidence_threshold=confidence_threshold,
        )
        buffer = io.BytesIO()
        annotated.save(buffer, format=output_format)
        buffer.seek(0)
        return buffer.getvalue()


# Singleton instance
_instance: Optional[OWLv2Detector] = None


def get_detector(model_name: str = "google/owlv2-base-patch16-ensemble") -> OWLv2Detector:
    """Get or create the OWLv2 detector singleton."""
    global _instance
    if _instance is None:
        _instance = OWLv2Detector(model_name=model_name)
    return _instance
