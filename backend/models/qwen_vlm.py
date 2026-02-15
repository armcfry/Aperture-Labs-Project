"""
Qwen VLM Model Wrapper
"""

import base64
import io
import requests
from PIL import Image


class QwenVLM:
    def __init__(
        self,
        model_name: str = "qwen2.5vl:7b",
        ollama_host: str = "http://localhost:11434"
    ):
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.is_loaded = False

    def load_model(self):
        print("Connecting to Ollama server")
        try:
            response = requests.get(f"{self.ollama_host}/api/tags")
            if response.status_code == 200:
                self.is_loaded = True
                print(f"Connected to Ollama at {self.ollama_host}")
            else:
                print(f"Ollama returned status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"Could not connect to Ollama at {self.ollama_host}")

    def detect_fod(self, image: Image.Image) -> str:
        if not self.is_loaded:
            self.load_model()

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

        response = requests.post(
            f"{self.ollama_host}/api/generate",
            json=payload
        )

        if response.status_code == 200:
            raw_response = response.json().get("response", "")
            print(raw_response)
            return raw_response
        else:
            print(f"Ollama error: {response.status_code}")
            return ""

    def _image_to_base64(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


model_instance = None

def get_model() -> QwenVLM:
    global model_instance
    if model_instance is None:
        model_instance = QwenVLM()
    return model_instance
