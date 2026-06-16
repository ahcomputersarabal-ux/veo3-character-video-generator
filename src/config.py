"""Configuration management for Veo 3 Video Generator"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field
import yaml


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Google Cloud
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    google_project_id: str = Field(default="", alias="GOOGLE_PROJECT_ID")
    google_cloud_bucket: str = Field(default="veo3-videos", alias="GOOGLE_CLOUD_BUCKET")

    # Veo 3 API
    veo3_model: str = Field(default="veo3-fast", alias="VEO3_MODEL")
    veo3_timeout: int = Field(default=300, alias="VEO3_TIMEOUT")
    veo3_max_retries: int = Field(default=3, alias="VEO3_MAX_RETRIES")

    # API Server
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_debug: bool = Field(default=False, alias="API_DEBUG")
    api_workers: int = Field(default=4, alias="API_WORKERS")

    # Storage
    storage_type: str = Field(default="local", alias="STORAGE_TYPE")
    storage_path: str = Field(default="./storage", alias="STORAGE_PATH")
    cache_dir: str = Field(default="./cache", alias="CACHE_DIR")

    # Character Settings
    character_consistency_threshold: float = Field(default=0.85, alias="CHARACTER_CONSISTENCY_THRESHOLD")
    character_max_references: int = Field(default=10, alias="CHARACTER_MAX_REFERENCES")

    # Video Settings
    video_default_duration: int = Field(default=6, alias="VIDEO_DEFAULT_DURATION")
    video_default_resolution: str = Field(default="4K", alias="VIDEO_DEFAULT_RESOLUTION")
    video_aspect_ratio: str = Field(default="16:9", alias="VIDEO_ASPECT_RATIO")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Security
    secret_key: str = Field(default="your_secret_key_here", alias="SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def validate_api_key(self) -> bool:
        """Validate that API key is configured"""
        return bool(self.google_api_key and self.google_api_key != "your_google_api_key_here"
                   )

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()


def load_yaml_config(path: str = "config.yaml") -> dict:
    """Load YAML configuration file"""
    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return yaml.safe_load(f) or {}
