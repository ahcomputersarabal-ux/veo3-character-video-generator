"""Frame extraction from video files"""

import os
from typing import List, Optional, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FrameData:
    """Extracted frame data"""
    frame_index: int
    timestamp: float  # in seconds
    image_array: np.ndarray
    height: int
    width: int
    extracted_at: str


class FrameExtractor:
    """Extracts frames from video files for consistency matching"""

    def __init__(self, output_dir: str = "./cache/frames", quality: int = 95):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.quality = quality

    def extract_last_frame(self, video_path: str) -> Optional[FrameData]:
        """
        Extract the last frame from a video file.

        Args:
            video_path: Path to video file

        Returns:
            FrameData containing the last frame
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        try:
            # Get total frame count
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Jump to last frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, total_frames - 1))
            ret, frame = cap.read()

            if not ret:
                raise RuntimeError("Failed to extract last frame")

            frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            timestamp = frame_index / fps if fps > 0 else 0

            return FrameData(
                frame_index=frame_index,
                timestamp=timestamp,
                image_array=frame,
                height=frame.shape[0],
                width=frame.shape[1],
                extracted_at=datetime.utcnow().isoformat()
            )

        finally:
            cap.release()

    def extract_frame_range(self, video_path: str, start_frame: int = 0,
                           end_frame: Optional[int] = None,
                           step: int = 1) -> List[FrameData]:
        """
        Extract a range of frames from a video.

        Args:
            video_path: Path to video file
            start_frame: Starting frame index
            end_frame: Ending frame index (None for all frames)
            step: Extract every nth frame

        Returns:
            List of FrameData objects
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        frames = []
        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            if end_frame is None:
                end_frame = total_frames

            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            frame_idx = start_frame

            while frame_idx < end_frame:
                ret, frame = cap.read()
                if not ret:
                    break

                timestamp = frame_idx / fps if fps > 0 else 0

                frames.append(FrameData(
                    frame_index=frame_idx,
                    timestamp=timestamp,
                    image_array=frame,
                    height=frame.shape[0],
                    width=frame.shape[1],
                    extracted_at=datetime.utcnow().isoformat()
                ))

                frame_idx += step
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

            return frames

        finally:
            cap.release()

    def save_frame(self, frame_data: FrameData, filename: str = None) -> str:
        """
        Save extracted frame to file.

        Args:
            frame_data: FrameData to save
            filename: Optional custom filename

        Returns:
            Path to saved frame file
        """
        if filename is None:
            filename = f"frame_{frame_data.frame_index:06d}.jpg"

        output_path = self.output_dir / filename
        cv2.imwrite(str(output_path), frame_data.image_array, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
        return str(output_path)

    def extract_keyframes(self, video_path: str, num_keyframes: int = 5) -> List[FrameData]:
        """
        Extract keyframes (evenly spaced) from video.

        Args:
            video_path: Path to video file
            num_keyframes: Number of keyframes to extract

        Returns:
            List of FrameData objects for keyframes
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            if total_frames <= num_keyframes:
                # If video is shorter than requested keyframes, extract all
                return self.extract_frame_range(video_path, 0, total_frames)

            step = max(1, total_frames // num_keyframes)
            return self.extract_frame_range(video_path, 0, total_frames, step)

        finally:
            cap.release()

    def get_video_metadata(self, video_path: str) -> dict:
        """
        Extract video metadata.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        try:
            return {
                "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "duration_seconds": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
            }
        finally:
            cap.release()
