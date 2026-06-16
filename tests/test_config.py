"""Test configuration"""

import pytest
from src.config import get_settings


def test_settings_loading():
    """Test settings loading"""
    settings = get_settings()
    assert settings is not None
    assert settings.veo3_model in ["veo3-fast", "veo3", "veo3.1"]
    assert settings.api_port > 0


def test_settings_caching():
    """Test that settings are cached"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
