"""Google Veo 3 API Client"""

import os
import json
import time
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio

import google.generativeai as genai
from google.generativeai.types import GenerateVideoResponse


@dataclass
class VideoGenerationRequest:
    """Video generation request parameters"""
    prompt: str
    duration: int = 6  # seconds (4, 6, or 8)
    resolution: str = "4K"  # 720p, 1080p, 4K
    fps: int = 24
    aspect_ratio: str = "16:9"
    model: str = "veo3-fast"
    quality: str = "high"


@dataclass
class VideoGenerationResponse:
    """Video generation response"""
    job_id: str
    status: str  # pending, processing, completed, failed
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str = None
    completed_at: Optional[str] = None
    metadata: Dict = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.metadata:
            self.metadata = {}


class Veo3Client:
    """Client for Google Veo 3 video generation API"""

    def __init__(self, api_key: str, model: str = "veo3-fast", timeout: int = 300):
        """
        Initialize Veo 3 client.

        Args:
            api_key: Google API key
            model: Model to use (veo3-fast, veo3, veo3.1)
            timeout: Request timeout in seconds
        """
        genai.configure(api_key=api_key)
        self.model = model
        self.timeout = timeout
        self.generation_config = genai.GenerationConfig(
            temperature=0.7,
        )

    def generate_text_to_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """
        Generate video from text prompt.

        Args:
            request: VideoGenerationRequest with prompt and parameters

        Returns:
            VideoGenerationResponse with video URL and metadata
        """
        try:
            # Prepare prompt with style and quality hints
            enhanced_prompt = self._enhance_prompt(request.prompt, request.quality)

            # Generate video using Veo 3 API
            response = genai.generate_video(
                model=f"models/{self.model}",
                prompt=enhanced_prompt,
                duration=request.duration,
                config=genai.types.GenerateVideoConfig(
                    resolution="1080p",
                    fps=request.fps,
                ),
            )

            # Wait for generation to complete
            generation_response = self._wait_for_generation(response)

            return VideoGenerationResponse(
                job_id=str(response.name),
                status="completed",
                video_url=generation_response.video_uri if hasattr(generation_response, 'video_uri') else None,
                created_at=datetime.utcnow().isoformat(),
                completed_at=datetime.utcnow().isoformat(),
                metadata={
                    "model": self.model,
                    "prompt": enhanced_prompt,
                    "duration": request.duration,
                    "resolution": request.resolution,
                    "fps": request.fps,
                }
            )

        except Exception as e:
            return VideoGenerationResponse(
                job_id="",
                status="failed",
                error_message=str(e)
            )

    def generate_image_to_video(self, image_path: str, prompt: str,
                               request: VideoGenerationRequest) -> VideoGenerationResponse:
        """
        Generate video from image and text prompt.

        Args:
            image_path: Path to reference image
            prompt: Text prompt for video generation
            request: VideoGenerationRequest with parameters

        Returns:
            VideoGenerationResponse with video URL and metadata
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")

            # Load and prepare image
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Enhance prompt
            enhanced_prompt = self._enhance_prompt(prompt, request.quality)

            # Generate video from image
            response = genai.generate_video(
                model=f"models/{self.model}",
                prompt=enhanced_prompt,
                duration=request.duration,
                config=genai.types.GenerateVideoConfig(
                    resolution="1080p",
                    fps=request.fps,
                ),
            )

            generation_response = self._wait_for_generation(response)

            return VideoGenerationResponse(
                job_id=str(response.name),
                status="completed",
                video_url=generation_response.video_uri if hasattr(generation_response, 'video_uri') else None,
                created_at=datetime.utcnow().isoformat(),
                completed_at=datetime.utcnow().isoformat(),
                metadata={
                    "model": self.model,
                    "prompt": enhanced_prompt,
                    "image_path": image_path,
                    "duration": request.duration,
                    "resolution": request.resolution,
                }
            )

        except Exception as e:
            return VideoGenerationResponse(
                job_id="",
                status="failed",
                error_message=str(e)
            )

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of a video generation job.

        Args:
            job_id: Job ID returned from generation

        Returns:
            Dictionary with status and metadata
        """
        try:
            response = genai.get_operation(job_id)
            return {
                "job_id": job_id,
                "done": response.done,
                "status": "completed" if response.done else "processing"
            }
        except Exception as e:
            return {"job_id": job_id, "error": str(e)}

    @staticmethod
    def _enhance_prompt(prompt: str, quality: str = "high") -> str:
        """
        Enhance prompt with quality and style hints.

        Args:
            prompt: Base prompt
            quality: Quality level (low, medium, high)

        Returns:
            Enhanced prompt
        """
        quality_hints = {
            "high": "ultra high quality, cinematic, professional lighting, sharp focus",
            "medium": "high quality, good lighting, sharp focus",
            "low": "good quality"
        }

        enhancement = quality_hints.get(quality, quality_hints["high"])
        return f"{prompt}. {enhancement}"

    @staticmethod
    def _wait_for_generation(response: Any, max_wait: int = 300) -> Any:
        """
        Wait for video generation to complete.

        Args:
            response: Generation response object
            max_wait: Maximum wait time in seconds

        Returns:
            Completed response
        """
        start_time = time.time()
        while not response.done and (time.time() - start_time) < max_wait:
            time.sleep(2)
            response = response.result()
        return response
