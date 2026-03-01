"""Tests for OWLv2 object detection module."""

import io
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


class TestOWLv2Detector:
    """Tests for OWLv2Detector class."""

    def test_detector_initialization(self):
        """Test OWLv2Detector initializes with correct defaults."""
        with patch("models.owlv2.Owlv2Processor"), patch("models.owlv2.Owlv2ForObjectDetection"):
            from models.owlv2 import OWLv2Detector

            detector = OWLv2Detector()
            assert detector.model_name == "google/owlv2-base-patch16-ensemble"
            assert detector.is_loaded is False

    def test_detector_custom_model_name(self):
        """Test OWLv2Detector accepts custom model name."""
        with patch("models.owlv2.Owlv2Processor"), patch("models.owlv2.Owlv2ForObjectDetection"):
            from models.owlv2 import OWLv2Detector

            detector = OWLv2Detector(model_name="google/owlv2-large-patch14-ensemble")
            assert detector.model_name == "google/owlv2-large-patch14-ensemble"

    def test_load_model_success(self):
        """Test load_model returns True on success."""
        with patch("models.owlv2.Owlv2Processor") as mock_processor, \
             patch("models.owlv2.Owlv2ForObjectDetection") as mock_model, \
             patch("models.owlv2.torch") as mock_torch:

            mock_torch.cuda.is_available.return_value = False
            mock_processor.from_pretrained.return_value = MagicMock()
            mock_model.from_pretrained.return_value = MagicMock()

            from models.owlv2 import OWLv2Detector

            detector = OWLv2Detector()
            result = detector.load_model()

            assert result is True
            assert detector.is_loaded is True
            mock_processor.from_pretrained.assert_called_once()
            mock_model.from_pretrained.assert_called_once()

    def test_load_model_failure(self):
        """Test load_model returns False on failure."""
        with patch("models.owlv2.Owlv2Processor") as mock_processor, \
             patch("models.owlv2.Owlv2ForObjectDetection"), \
             patch("models.owlv2.torch") as mock_torch:

            mock_torch.cuda.is_available.return_value = False
            mock_processor.from_pretrained.side_effect = Exception("Model not found")

            from models.owlv2 import OWLv2Detector

            detector = OWLv2Detector()
            result = detector.load_model()

            assert result is False
            assert detector.is_loaded is False

    def test_detect_and_draw_returns_image(self):
        """Test detect_and_draw returns a PIL Image."""
        with patch("models.owlv2.Owlv2Processor") as mock_processor_cls, \
             patch("models.owlv2.Owlv2ForObjectDetection") as mock_model_cls, \
             patch("models.owlv2.torch") as mock_torch:

            # Setup mocks
            mock_torch.cuda.is_available.return_value = False
            mock_torch.no_grad.return_value.__enter__ = MagicMock()
            mock_torch.no_grad.return_value.__exit__ = MagicMock()
            mock_torch.tensor.return_value = MagicMock()

            mock_processor = MagicMock()
            mock_processor_cls.from_pretrained.return_value = mock_processor
            mock_processor.return_value = {"input_ids": MagicMock()}
            mock_processor.post_process_object_detection.return_value = [{
                "boxes": MagicMock(cpu=lambda: MagicMock(numpy=lambda: [])),
                "scores": MagicMock(cpu=lambda: MagicMock(numpy=lambda: [])),
                "labels": MagicMock(cpu=lambda: MagicMock(numpy=lambda: [])),
            }]

            mock_model = MagicMock()
            mock_model_cls.from_pretrained.return_value = mock_model

            from models.owlv2 import OWLv2Detector

            detector = OWLv2Detector()
            test_image = Image.new("RGB", (100, 100), color="blue")

            result = detector.detect_and_draw(
                image=test_image,
                text_queries=["object"],
            )

            assert isinstance(result, Image.Image)
            assert result.size == test_image.size

    def test_detect_and_draw_bytes_returns_bytes(self):
        """Test detect_and_draw_bytes returns bytes."""
        with patch("models.owlv2.Owlv2Processor") as mock_processor_cls, \
             patch("models.owlv2.Owlv2ForObjectDetection") as mock_model_cls, \
             patch("models.owlv2.torch") as mock_torch:

            # Setup mocks
            mock_torch.cuda.is_available.return_value = False
            mock_torch.no_grad.return_value.__enter__ = MagicMock()
            mock_torch.no_grad.return_value.__exit__ = MagicMock()
            mock_torch.tensor.return_value = MagicMock()

            mock_processor = MagicMock()
            mock_processor_cls.from_pretrained.return_value = mock_processor
            mock_processor.return_value = {"input_ids": MagicMock()}
            mock_processor.post_process_object_detection.return_value = [{
                "boxes": MagicMock(cpu=lambda: MagicMock(numpy=lambda: [])),
                "scores": MagicMock(cpu=lambda: MagicMock(numpy=lambda: [])),
                "labels": MagicMock(cpu=lambda: MagicMock(numpy=lambda: [])),
            }]

            mock_model = MagicMock()
            mock_model_cls.from_pretrained.return_value = mock_model

            from models.owlv2 import OWLv2Detector

            detector = OWLv2Detector()
            test_image = Image.new("RGB", (100, 100), color="green")

            result = detector.detect_and_draw_bytes(
                image=test_image,
                text_queries=["debris"],
                output_format="PNG",
            )

            assert isinstance(result, bytes)
            assert len(result) > 0
            # Verify it's a valid PNG
            img = Image.open(io.BytesIO(result))
            assert img.format == "PNG"

    def test_get_detector_singleton(self):
        """Test get_detector returns singleton instance."""
        with patch("models.owlv2.Owlv2Processor"), \
             patch("models.owlv2.Owlv2ForObjectDetection"), \
             patch("models.owlv2.torch"):

            # Reset singleton
            import models.owlv2 as owlv2_module
            owlv2_module._instance = None

            from models.owlv2 import get_detector

            detector1 = get_detector()
            detector2 = get_detector()

            assert detector1 is detector2


class TestOWLv2Router:
    """Tests for OWLv2 router endpoints."""

    def test_detect_endpoint_returns_image(self, client, sample_image_bytes):
        """Test /owlv2/detect endpoint returns an image."""
        with patch("routers.owlv2.get_detector") as mock_get_detector:
            # Create a mock detector that returns a valid PNG
            mock_detector = MagicMock()
            test_output = Image.new("RGB", (100, 100), color="red")
            buffer = io.BytesIO()
            test_output.save(buffer, format="PNG")
            mock_detector.detect_and_draw_bytes.return_value = buffer.getvalue()
            mock_get_detector.return_value = mock_detector

            response = client.post(
                "/owlv2/detect",
                files={"file": ("test.png", sample_image_bytes, "image/png")},
                params={"queries": "bolt,debris", "confidence": 0.2},
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            # Verify response is a valid image
            img = Image.open(io.BytesIO(response.content))
            assert img.format == "PNG"

    def test_detect_endpoint_default_queries(self, client, sample_image_bytes):
        """Test /owlv2/detect uses default queries when not specified."""
        with patch("routers.owlv2.get_detector") as mock_get_detector:
            mock_detector = MagicMock()
            test_output = Image.new("RGB", (100, 100), color="blue")
            buffer = io.BytesIO()
            test_output.save(buffer, format="PNG")
            mock_detector.detect_and_draw_bytes.return_value = buffer.getvalue()
            mock_get_detector.return_value = mock_detector

            response = client.post(
                "/owlv2/detect",
                files={"file": ("test.png", sample_image_bytes, "image/png")},
            )

            assert response.status_code == 200
            # Verify default queries were used
            call_args = mock_detector.detect_and_draw_bytes.call_args
            text_queries = call_args.kwargs.get("text_queries") or call_args[1].get("text_queries")
            assert "foreign object" in text_queries
            assert "debris" in text_queries

    def test_detect_endpoint_custom_confidence(self, client, sample_image_bytes):
        """Test /owlv2/detect accepts custom confidence threshold."""
        with patch("routers.owlv2.get_detector") as mock_get_detector:
            mock_detector = MagicMock()
            test_output = Image.new("RGB", (100, 100), color="green")
            buffer = io.BytesIO()
            test_output.save(buffer, format="PNG")
            mock_detector.detect_and_draw_bytes.return_value = buffer.getvalue()
            mock_get_detector.return_value = mock_detector

            response = client.post(
                "/owlv2/detect",
                files={"file": ("test.png", sample_image_bytes, "image/png")},
                params={"confidence": 0.5},
            )

            assert response.status_code == 200
            # Verify custom confidence was used
            call_args = mock_detector.detect_and_draw_bytes.call_args
            confidence = call_args.kwargs.get("confidence_threshold") or call_args[1].get("confidence_threshold")
            assert confidence == 0.5

    def test_detect_endpoint_invalid_confidence_too_high(self, client, sample_image_bytes):
        """Test /owlv2/detect rejects confidence > 1."""
        response = client.post(
            "/owlv2/detect",
            files={"file": ("test.png", sample_image_bytes, "image/png")},
            params={"confidence": 1.5},
        )

        assert response.status_code == 422  # Validation error

    def test_detect_endpoint_invalid_confidence_negative(self, client, sample_image_bytes):
        """Test /owlv2/detect rejects negative confidence."""
        response = client.post(
            "/owlv2/detect",
            files={"file": ("test.png", sample_image_bytes, "image/png")},
            params={"confidence": -0.1},
        )

        assert response.status_code == 422  # Validation error

    def test_detect_endpoint_missing_file(self, client):
        """Test /owlv2/detect returns 422 when file is missing."""
        response = client.post("/owlv2/detect")

        assert response.status_code == 422  # Validation error

    def test_detect_endpoint_jpeg_image(self, client):
        """Test /owlv2/detect accepts JPEG images."""
        with patch("routers.owlv2.get_detector") as mock_get_detector:
            mock_detector = MagicMock()
            test_output = Image.new("RGB", (100, 100), color="yellow")
            buffer = io.BytesIO()
            test_output.save(buffer, format="PNG")
            mock_detector.detect_and_draw_bytes.return_value = buffer.getvalue()
            mock_get_detector.return_value = mock_detector

            # Create JPEG image
            jpeg_image = Image.new("RGB", (100, 100), color="purple")
            jpeg_buffer = io.BytesIO()
            jpeg_image.save(jpeg_buffer, format="JPEG")
            jpeg_bytes = jpeg_buffer.getvalue()

            response = client.post(
                "/owlv2/detect",
                files={"file": ("test.jpg", jpeg_bytes, "image/jpeg")},
            )

            assert response.status_code == 200
