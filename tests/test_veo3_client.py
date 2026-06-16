"""Unit tests for Veo3 client"""

import pytest
from unittest.mock import Mock, patch
from src.video.veo3_client import Veo3Client, VideoGenerationRequest


@pytest.fixture
def veo3_client():
    """Create Veo3 client with mock API key"""
    return Veo3Client(api_key="test_api_key", model="veo3-fast")


class TestVeo3Client:
    """Test cases for Veo3Client"""

    def test_client_initialization(self, veo3_client):
        """Test client initialization"""
        assert veo3_client.model == "veo3-fast"
        assert veo3_client.timeout == 300

    def test_enhance_prompt(self):
        """Test prompt enhancement"""
        prompt = "A woman walking"
        enhanced = Veo3Client._enhance_prompt(prompt, "high")

        assert "woman walking" in enhanced
        assert "ultra high quality" in enhanced
        assert "cinematic" in enhanced

    def test_video_generation_request_validation(self):
        """Test request validation"""
        request = VideoGenerationRequest(
            prompt="Test prompt",
            duration=6,
            resolution="4K"
        )

        assert request.prompt == "Test prompt"
        assert request.duration == 6
        assert request.resolution == "4K"
        assert request.model == "veo3-fast"
