"""LM Studio API client for text and vision analysis."""

import base64
import json
from pathlib import Path
from typing import Dict, Optional

import requests


class LMStudioClient:
    """Client for interacting with LM Studio API."""

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        text_model: str = "qwen2.5-7b-instruct",
        vision_model: str = "mlx-community/SmolVLM-500M-Instruct-4bit",
        temperature: float = 0.3,
        max_tokens: int = 150,
    ):
        """
        Initialize LM Studio client.

        Args:
            base_url: LM Studio API base URL
            text_model: Model name for text analysis
            vision_model: Model name for vision analysis
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.base_url = base_url
        self.text_model = text_model
        self.vision_model = vision_model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def analyze_text(self, text: str, prompt: str) -> Optional[Dict]:
        """
        Analyze text content to extract filename components.

        Args:
            text: Text content to analyze
            prompt: System prompt for analysis

        Returns:
            Dictionary with filename components or None on error
        """
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.text_model,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text},
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
                timeout=30,
            )

            if response.status_code != 200:
                print(f"Error: API returned status {response.status_code}")
                return None

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Try to parse JSON response
            # Handle markdown code blocks
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            return json.loads(content)

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response was: {content}")
            return None
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return None

    def analyze_image(self, image_path: str, prompt: str) -> Optional[Dict]:
        """
        Analyze image content to extract filename components.

        Args:
            image_path: Path to image file
            prompt: System prompt for analysis

        Returns:
            Dictionary with filename components or None on error
        """
        try:
            # Read and encode image as base64
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Determine image format
            ext = Path(image_path).suffix.lower()
            mime_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }.get(ext, "image/jpeg")

            # Send to LM Studio vision model
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.vision_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{image_data}"
                                    },
                                },
                            ],
                        }
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
                timeout=30,
            )

            if response.status_code != 200:
                print(f"Error: API returned status {response.status_code}")
                print(f"Response: {response.text}")
                return None

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse JSON response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            return json.loads(content)

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response was: {content}")
            return None
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test connection to LM Studio.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"Connected to LM Studio. Available models: {len(data['data'])}")
                for model in data["data"]:
                    print(f"  - {model['id']}")
                return True
            else:
                print(f"Error: API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"Error connecting to LM Studio: {e}")
            return False
