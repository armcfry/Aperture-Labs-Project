"""Tests for ollama_vlm (VLM detection and response parsing)."""
import base64
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

from models.ollama_vlm import (
    _parse_pass_fail,
    _parse_defects_from_response,
    get_mock_detection_response,
    OllamaVLM,
    get_model,
)

pytestmark = pytest.mark.unit


class TestParsePassFail:
    def test_result_pass_lower(self):
        assert _parse_pass_fail("summary\nRESULT: PASS") == "pass"
        assert _parse_pass_fail("RESULT: PASS") == "pass"

    def test_result_pass_no_space(self):
        assert _parse_pass_fail("RESULT:PASS") == "pass"

    def test_result_fail(self):
        assert _parse_pass_fail("RESULT: FAIL") == "fail"
        assert _parse_pass_fail("RESULT:FAIL") == "fail"

    def test_out_of_scope_returns_fail(self):
        assert _parse_pass_fail("Image is out of scope for inspection.") == "fail"
        assert _parse_pass_fail("Does not show a runway.") == "fail"

    def test_no_fod_returns_pass(self):
        assert _parse_pass_fail("No FOD detected. Clear.") == "pass"
        assert _parse_pass_fail("No foreign object. RESULT: PASS") == "pass"

    def test_fod_mentioned_returns_fail(self):
        assert _parse_pass_fail("FOD detected at 10%, 20%.") == "fail"
        assert _parse_pass_fail("Foreign object debris found.") == "fail"

    def test_fallback_fail(self):
        # Must not contain "clear", "pass", "fail", "fod", etc. to hit default
        assert _parse_pass_fail("Inconclusive or unknown.") == "fail"


class TestParseDefectsFromResponse:
    def test_parses_critical_and_major_bullets(self):
        text = """CRITICAL FAILURES:
• First defect description
MAJOR ISSUES:
• Second defect"""
        defects = _parse_defects_from_response(text)
        assert len(defects) >= 1
        assert defects[0].severity in ("critical", "major")
        assert "defect" in defects[0].description.lower() or "first" in defects[0].description.lower()

    def test_fallback_defect_when_fod_mentioned(self):
        text = "FOD detected in the image. No structured list."
        defects = _parse_defects_from_response(text)
        assert len(defects) == 1
        assert defects[0].id == "DEF-001"
        assert defects[0].severity in ("critical", "major")

    def test_empty_response_no_defects(self):
        text = "Nothing relevant here."
        defects = _parse_defects_from_response(text)
        assert defects == []


class TestGetMockDetectionResponse:
    def test_returns_detection_response(self):
        resp = get_mock_detection_response()
        assert resp.response
        assert resp.model
        assert resp.inference_time_ms == 0
        assert resp.pass_fail == "fail"
        assert resp.defects is not None
        assert len(resp.defects) >= 1
        assert resp.prompt_used


class TestOllamaVLM:
    def test_init_default_model(self):
        vlm = OllamaVLM()
        assert vlm.model_name
        assert vlm.ollama_host == "http://localhost:11434"
        assert vlm.is_loaded is False

    def test_init_custom_model_and_host(self):
        vlm = OllamaVLM(model_name="custom:7b", ollama_host="http://host:9999")
        assert vlm.model_name == "custom:7b"
        assert vlm.ollama_host == "http://host:9999"

    @patch("models.ollama_vlm.requests.get")
    def test_load_model_success(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        vlm = OllamaVLM(model_name="test")
        result = vlm.load_model()
        assert result is True
        assert vlm.is_loaded is True

    @patch("models.ollama_vlm.requests.get")
    def test_load_model_connection_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        vlm = OllamaVLM(model_name="test")
        result = vlm.load_model()
        assert result is False
        assert vlm.is_loaded is False

    @patch("models.ollama_vlm.requests.get")
    def test_load_model_non_200(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500)
        vlm = OllamaVLM(model_name="test")
        result = vlm.load_model()
        assert result is False

    def test_default_generic_prompt(self):
        vlm = OllamaVLM(model_name="test")
        prompt = vlm._default_generic_prompt()
        assert "quality inspector" in prompt.lower()
        assert "RESULT: PASS" in prompt
        assert "RESULT: FAIL" in prompt

    def test_build_spec_prompt(self):
        vlm = OllamaVLM(model_name="test")
        prompt = vlm._build_spec_prompt("Spec text here.")
        assert "Spec text here." in prompt
        assert "Specification" in prompt

    def test_image_to_base64(self):
        vlm = OllamaVLM(model_name="test")
        img = Image.new("RGB", (10, 10), color="red")
        b64 = vlm._image_to_base64(img)
        decoded = base64.b64decode(b64)
        assert decoded[:8] == b"\x89PNG\r\n\x1a\n"

    def test_get_prompt_for_spec_with_spec(self):
        vlm = OllamaVLM(model_name="test")
        prompt = vlm.get_prompt_for_spec("My spec.")
        assert "My spec." in prompt

    def test_get_prompt_for_spec_without_spec(self):
        vlm = OllamaVLM(model_name="test")
        prompt = vlm.get_prompt_for_spec(None)
        assert vlm._default_generic_prompt() == prompt
        prompt2 = vlm.get_prompt_for_spec("   ")
        assert vlm._default_generic_prompt() == prompt2

    @patch("models.ollama_vlm.requests.get")
    @patch("models.ollama_vlm.requests.post")
    def test_detect_fod_success(self, mock_post, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": "No defects. RESULT: PASS"},
        )
        vlm = OllamaVLM(model_name="test")
        img = Image.new("RGB", (32, 32), color="white")
        resp = vlm.detect_fod(img)
        assert resp.pass_fail == "pass"
        assert resp.model == "test"
        assert resp.inference_time_ms >= 0

    @patch("models.ollama_vlm.requests.get")
    @patch("models.ollama_vlm.requests.post")
    def test_detect_fod_api_error_returns_fail(self, mock_post, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        mock_post.return_value = MagicMock(status_code=500)
        vlm = OllamaVLM(model_name="test")
        img = Image.new("RGB", (32, 32), color="white")
        resp = vlm.detect_fod(img)
        assert resp.pass_fail == "fail"
        assert resp.defects
        assert "500" in resp.response or "Error" in resp.response


class TestGetModel:
    def test_get_model_singleton_per_name(self):
        m1 = get_model("singleton-test")
        m2 = get_model("singleton-test")
        assert m1 is m2

    def test_get_model_different_names_different_instances(self):
        m1 = get_model("model-a")
        m2 = get_model("model-b")
        assert m1 is not m2
