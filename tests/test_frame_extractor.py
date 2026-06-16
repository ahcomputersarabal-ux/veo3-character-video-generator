"""Unit tests for frame extractor"""

import pytest
import tempfile
import cv2
import numpy as np
from pathlib import Path
from src.video.frame_extractor import FrameExtractor


@pytest.fixture
def temp_video():
    """Create a temporary test video"""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        video_path = f.name

    # Create a simple video file
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 24.0, (640, 480))

    # Write 10 frames
    for i in range(10):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        out.write(frame)

    out.release()
    yield video_path

    # Cleanup
    Path(video_path).unlink()


@pytest.fixture
def frame_extractor(tmp_path):
    """Create frame extractor with temp directory"""
    return FrameExtractor(output_dir=str(tmp_path))


class TestFrameExtractor:
    """Test cases for FrameExtractor"""

    def test_extract_last_frame(self, frame_extractor, temp_video):
        """Test extracting the last frame"""
        frame_data = frame_extractor.extract_last_frame(temp_video)

        assert frame_data is not None
        assert frame_data.image_array is not None
        assert frame_data.height == 480
        assert frame_data.width == 640

    def test_get_video_metadata(self, frame_extractor, temp_video):
        """Test getting video metadata"""
        metadata = frame_extractor.get_video_metadata(temp_video)

        assert metadata["total_frames"] == 10
        assert metadata["fps"] == 24.0
        assert metadata["width"] == 640
        assert metadata["height"] == 480

    def test_extract_nonexistent_video(self, frame_extractor):
        """Test extracting from nonexistent video"""
        with pytest.raises(FileNotFoundError):
            frame_extractor.extract_last_frame("nonexistent.mp4")
