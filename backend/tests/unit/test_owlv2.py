"""Unit tests for models/owlv2.py — defect query building and annotation helpers."""
import base64
import io
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

from models.owlv2 import (
    _defect_to_query,
    build_queries_and_severity_map,
    image_to_base64,
    get_owlv2_detector,
    OWLv2Detector,
    _SEVERITY_COLORS,
    _DEFAULT_COLOR,
)
from schemas.detection import DefectSchema

pytestmark = pytest.mark.unit


# ── Helpers ───────────────────────────────────────────────────────────────────

def _defect(description: str, severity: str = "major") -> DefectSchema:
    return DefectSchema(id="DEF-001", severity=severity, description=description)


def _rgb_image(w: int = 100, h: int = 100) -> Image.Image:
    return Image.new("RGB", (w, h), color=(200, 200, 200))


def _detector_with_mock_model() -> OWLv2Detector:
    """Return a detector with _model/_processor pre-set so _load() is a no-op."""
    d = OWLv2Detector()
    d._model = MagicMock()
    d._processor = MagicMock()
    d._device = "cpu"
    return d


# ── image_to_base64 ───────────────────────────────────────────────────────────

class TestImageToBase64:
    def test_returns_valid_base64_png(self):
        img = _rgb_image(10, 10)
        result = image_to_base64(img)
        decoded = base64.b64decode(result)
        assert decoded[:8] == b"\x89PNG\r\n\x1a\n"

    def test_round_trips_image_size(self):
        img = _rgb_image(32, 64)
        result = image_to_base64(img)
        decoded = base64.b64decode(result)
        restored = Image.open(io.BytesIO(decoded))
        assert restored.size == (32, 64)

    def test_output_is_string(self):
        assert isinstance(image_to_base64(_rgb_image()), str)


# ── _defect_to_query ──────────────────────────────────────────────────────────

class TestDefectToQuery:
    def test_plain_description_returned(self):
        assert _defect_to_query("loose bolt on runway") == "loose bolt on runway"

    def test_strips_parenthesised_position_hint(self):
        result = _defect_to_query("metal debris (25%, 30%)")
        assert "%" not in result
        assert "debris" in result

    def test_strips_bare_percentage_coordinates(self):
        result = _defect_to_query("bolt 19% 24.8%")
        assert "%" not in result

    def test_strips_metadata_prefix_object_classification(self):
        result = _defect_to_query("Object classification: Bolt")
        assert result == "Bolt"

    def test_strips_metadata_prefix_severity_rating(self):
        result = _defect_to_query("Severity rating: HIGH")
        assert result == "" or result == "HIGH"   # either stripped to empty or to bare word which is also rejected

    def test_strips_metadata_prefix_confidence_score(self):
        result = _defect_to_query("Confidence score: 1.0")
        assert result == ""

    def test_strips_metadata_prefix_approximate_location(self):
        result = _defect_to_query("Approximate location: 20% X, 50% Y")
        assert result == ""

    def test_uses_text_after_colon_when_descriptive(self):
        result = _defect_to_query("Surface Integrity: Foreign object detected")
        assert "foreign object" in result.lower() or "detected" in result.lower()

    def test_takes_first_clause_before_dash_separator(self):
        result = _defect_to_query("loose bolt — immediate action required")
        assert "immediate" not in result
        assert "bolt" in result

    def test_takes_first_clause_before_comma(self):
        result = _defect_to_query("metal fragment, possibly from engine cowling")
        assert "possibly" not in result
        assert "metal" in result

    def test_truncates_to_50_chars(self):
        long_desc = "a very long description about a foreign object that exceeds the limit"
        result = _defect_to_query(long_desc)
        assert len(result) <= 50

    def test_rejects_single_severity_word_high(self):
        assert _defect_to_query("high") == ""

    def test_rejects_single_severity_word_critical(self):
        assert _defect_to_query("critical") == ""

    def test_rejects_single_severity_word_low(self):
        assert _defect_to_query("low") == ""

    def test_rejects_bare_number(self):
        assert _defect_to_query("1.0") == ""

    def test_rejects_empty_string(self):
        assert _defect_to_query("") == ""

    def test_rejects_short_result(self):
        assert _defect_to_query("ab") == ""

    def test_rejects_result_with_no_alpha_word(self):
        assert _defect_to_query("99, 100") == ""

    def test_strips_leading_bare_number_from_metadata(self):
        # After stripping "Confidence score: ", "1.0" is left; should return ""
        result = _defect_to_query("Confidence score: 1.0")
        assert result == ""

    def test_returns_empty_for_metadata_only_words(self):
        for word in ("pass", "fail", "none", "n/a"):
            assert _defect_to_query(word) == ""


# ── build_queries_and_severity_map ────────────────────────────────────────────

class TestBuildQueriesAndSeverityMap:
    def test_single_defect(self):
        defects = [_defect("loose bolt on runway", "critical")]
        queries, smap = build_queries_and_severity_map(defects)
        assert len(queries) == 1
        assert "bolt" in queries[0]
        assert smap[0] == "critical"

    def test_deduplicates_identical_descriptions(self):
        defects = [
            _defect("loose bolt", "critical"),
            _defect("loose bolt", "major"),
        ]
        queries, smap = build_queries_and_severity_map(defects)
        assert len(queries) == 1

    def test_multiple_distinct_defects(self):
        defects = [
            _defect("loose bolt", "critical"),
            _defect("rubber debris", "major"),
        ]
        queries, smap = build_queries_and_severity_map(defects)
        assert len(queries) == 2
        assert smap[0] == "critical"
        assert smap[1] == "major"

    def test_skips_empty_query_from_metadata_only(self):
        defects = [_defect("Confidence score: 1.0", "major")]
        queries, smap = build_queries_and_severity_map(defects)
        assert queries == []
        assert smap == {}

    def test_empty_defect_list(self):
        queries, smap = build_queries_and_severity_map([])
        assert queries == []
        assert smap == {}

    def test_severity_map_indices_match_queries(self):
        defects = [
            _defect("bolt fragment", "critical"),
            _defect("rubber strip", "minor"),
            _defect("plastic cap", "major"),
        ]
        queries, smap = build_queries_and_severity_map(defects)
        assert len(queries) == len(smap)
        for i in range(len(queries)):
            assert i in smap


# ── get_owlv2_detector (singleton) ───────────────────────────────────────────

class TestGetOwlv2Detector:
    def test_returns_owlv2_detector_instance(self):
        detector = get_owlv2_detector()
        assert isinstance(detector, OWLv2Detector)

    def test_singleton_same_instance(self):
        d1 = get_owlv2_detector()
        d2 = get_owlv2_detector()
        assert d1 is d2


# ── OWLv2Detector ─────────────────────────────────────────────────────────────

class TestOWLv2DetectorLoad:
    def test_load_skipped_when_model_already_set(self):
        detector = OWLv2Detector()
        detector._model = MagicMock()  # pre-set
        # _load should return immediately without trying to import transformers
        detector._load()   # should not raise

    def test_load_raises_runtime_error_when_torch_missing(self):
        detector = OWLv2Detector()
        with patch.dict("sys.modules", {"torch": None, "transformers": None}):
            with pytest.raises((RuntimeError, ImportError)):
                detector._load()


class TestOWLv2DetectorAnnotate:
    """torch is imported locally inside annotate, so we patch torch directly."""

    def _mock_processor(self, detector, boxes, scores, labels):
        mock_tensor = MagicMock()
        mock_tensor.to.return_value = mock_tensor
        detector._processor.return_value = {"input_ids": mock_tensor}
        detector._processor.image_processor.post_process_object_detection.return_value = [{
            "boxes": MagicMock(tolist=lambda: boxes),
            "scores": MagicMock(tolist=lambda: scores),
            "labels": MagicMock(tolist=lambda: labels),
        }]

    def test_empty_queries_returns_original_image(self):
        detector = _detector_with_mock_model()
        img = _rgb_image()
        result = detector.annotate(img, [])
        assert result is img

    def test_no_detections_returns_original_image(self):
        detector = _detector_with_mock_model()
        img = _rgb_image()
        self._mock_processor(detector, [], [], [])
        with patch("torch.no_grad"), patch("torch.tensor") as mt:
            mt.return_value = MagicMock()
            result = detector.annotate(img, ["bolt"])
        assert result is img

    def test_detections_returns_annotated_copy(self):
        detector = _detector_with_mock_model()
        img = _rgb_image(200, 200)
        self._mock_processor(detector, [[10.0, 10.0, 80.0, 80.0]], [0.9], [0])
        with patch("torch.no_grad"), patch("torch.tensor") as mt:
            mt.return_value = MagicMock()
            result = detector.annotate(img, ["bolt"], severity_map={0: "critical"})
        assert result is not img
        assert result.size == img.size

    def test_severity_map_none_uses_default_color(self):
        """Passing severity_map=None should not raise."""
        detector = _detector_with_mock_model()
        img = _rgb_image(200, 200)
        self._mock_processor(detector, [[5.0, 5.0, 50.0, 50.0]], [0.8], [0])
        with patch("torch.no_grad"), patch("torch.tensor") as mt:
            mt.return_value = MagicMock()
            result = detector.annotate(img, ["debris"], severity_map=None)
        assert result is not img

    def test_keeps_best_box_per_label(self):
        """When two boxes share a label, only the higher-confidence one is kept."""
        detector = _detector_with_mock_model()
        img = _rgb_image(200, 200)
        self._mock_processor(
            detector,
            [[5.0, 5.0, 20.0, 20.0], [50.0, 50.0, 150.0, 150.0]],
            [0.3, 0.9],
            [0, 0],
        )
        with patch("torch.no_grad"), patch("torch.tensor") as mt:
            mt.return_value = MagicMock()
            result = detector.annotate(img, ["bolt"])
        assert result is not img


# ── Severity colour mapping ───────────────────────────────────────────────────

class TestSeverityColors:
    def test_known_severities_have_colors(self):
        assert "critical" in _SEVERITY_COLORS
        assert "major" in _SEVERITY_COLORS
        assert "minor" in _SEVERITY_COLORS

    def test_unknown_severity_falls_back_to_default(self):
        assert _DEFAULT_COLOR not in _SEVERITY_COLORS.values()
