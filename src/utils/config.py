"""Configuration management for file-renamer."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """Configuration manager for file-renamer."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config file. Defaults to config.yaml in project root.
        """
        if config_path is None:
            # Look for config.yaml in project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.yaml"

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}\n"
                f"Please copy config.example.yaml to config.yaml and configure it."
            )

        with open(self.config_path, "r") as f:
            self._config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'lm_studio.base_url')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    @property
    def lm_studio_url(self) -> str:
        """Get LM Studio base URL."""
        return self.get("lm_studio.base_url", "http://localhost:1234/v1")

    @property
    def text_model(self) -> str:
        """Get text analysis model name."""
        return self.get("lm_studio.text_model", "qwen2.5-7b-instruct")

    @property
    def vision_model(self) -> str:
        """Get vision analysis model name."""
        return self.get("lm_studio.vision_model", "mlx-community/SmolVLM-500M-Instruct-4bit")

    @property
    def temperature(self) -> float:
        """Get model temperature."""
        return self.get("lm_studio.temperature", 0.3)

    @property
    def max_tokens(self) -> int:
        """Get max tokens for generation."""
        return self.get("lm_studio.max_tokens", 150)

    @property
    def case_style(self) -> str:
        """Get filename case style."""
        return self.get("naming.case_style", "kebab")

    @property
    def date_format(self) -> str:
        """Get date format."""
        return self.get("naming.date_format", "yyyymmdd")

    @property
    def date_position(self) -> str:
        """Get date position in filename."""
        return self.get("naming.date_position", "end")

    @property
    def max_filename_length(self) -> int:
        """Get maximum filename length."""
        return self.get("naming.max_length", 100)

    @property
    def dry_run(self) -> bool:
        """Check if in dry-run mode."""
        return self.get("processing.dry_run", False)

    @property
    def create_backup(self) -> bool:
        """Check if backups should be created."""
        return self.get("processing.create_backup", True)

    @property
    def skip_already_formatted(self) -> bool:
        """Check if already-formatted files should be skipped."""
        return self.get("processing.skip_already_formatted", True)

    @property
    def supported_documents(self) -> list:
        """Get supported document extensions."""
        return self.get("file_types.documents", [])

    @property
    def supported_images(self) -> list:
        """Get supported image extensions."""
        return self.get("file_types.images", [])

    @property
    def supported_videos(self) -> list:
        """Get supported video extensions."""
        return self.get("file_types.videos", [])

    @property
    def text_prompt(self) -> str:
        """Get text analysis prompt."""
        return self.get("prompts.text_instruction", "")

    @property
    def vision_prompt(self) -> str:
        """Get vision analysis prompt."""
        return self.get("prompts.vision_instruction", "")

    def all_supported_extensions(self) -> list:
        """Get all supported file extensions."""
        return (
            self.supported_documents + self.supported_images + self.supported_videos
        )

    def is_document(self, file_path: Path) -> bool:
        """Check if file is a document."""
        return file_path.suffix.lower() in self.supported_documents

    def is_image(self, file_path: Path) -> bool:
        """Check if file is an image."""
        return file_path.suffix.lower() in self.supported_images

    def is_video(self, file_path: Path) -> bool:
        """Check if file is a video."""
        return file_path.suffix.lower() in self.supported_videos
