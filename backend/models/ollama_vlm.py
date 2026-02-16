"""
Ollama-based VLM for FOD Detection
"""

import base64
import io
import time
from typing import Optional
from dataclasses import dataclass

import requests
from PIL import Image


@dataclass
class DetectionResult:
    """
    Class to track state
    """
    raw_response: str
    model_name: str
    inference_time_ms: float

    def __str__(self) -> str:
        return self.raw_response


class OllamaVLM:
    def __init__(
        self,
        model_name: str = "qwen2.5vl:7b",
        ollama_host: str = "http://localhost:11434"
    ):
        self.model_name = model_name
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

    def detect_fod(self, image: Image.Image, prompt: Optional[str] = None) -> DetectionResult:
        """
        Analyze an image for Foreign Object Debris using the configured VLM.

        Args:
            image: PIL Image to analyze to be converted to base64 PNG.
            prompt: Custom prompt for the VLM. If None, uses default FOD detection prompt.

        Returns:
            DetectionResult containing the model's response, model name, and inference time.
        """
        if not self.is_loaded:
            self.load_model()

        if prompt is None:
            prompt = (
                "Identify all instances of Foreign Object Debris (FOD) in this image. "
                "For each item, describe what it is and specify its approximate location."
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
            return DetectionResult(
                raw_response=raw_response,
                model_name=self.model_name,
                inference_time_ms=inference_time
            )
        else:
            error = f"Error: {response.status_code}"
            return DetectionResult(
                raw_response=error,
                model_name=self.model_name,
                inference_time_ms=inference_time
            )

    def _image_to_base64(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


# Singleton ensures that there's only one instance of OllmaVLM. Used by get_model()
_instances: dict[str, OllamaVLM] = {}

def get_model(model_name: str = "qwen2.5vl:7b") -> OllamaVLM:
    if model_name not in _instances:
        _instances[model_name] = OllamaVLM(model_name=model_name)
    return _instances[model_name]
