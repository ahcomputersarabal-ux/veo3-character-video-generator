"""Example: Basic text-to-video generation"""

import os
from src.config import get_settings
from src.video.veo3_client import Veo3Client, VideoGenerationRequest


def main():
    # Load settings from .env
    settings = get_settings()

    if not settings.validate_api_key():
        print("Error: Google API key not configured")
        print("Please set GOOGLE_API_KEY in .env file")
        return

    # Initialize Veo 3 client
    client = Veo3Client(
        api_key=settings.google_api_key,
        model=settings.veo3_model,
        timeout=settings.veo3_timeout
    )

    # Create video generation request
    request = VideoGenerationRequest(
        prompt="A woman with long dark hair walking through a lush forest at sunset, wearing a blue dress, cinematic lighting",
        duration=6,
        resolution="4K",
        fps=24,
        model="veo3-fast",
        quality="high"
    )

    print("Generating video...")
    print(f"Prompt: {request.prompt}")
    print(f"Duration: {request.duration}s")
    print(f"Resolution: {request.resolution}")

    # Generate video
    response = client.generate_text_to_video(request)

    print(f"\nGeneration Result:")
    print(f"Job ID: {response.job_id}")
    print(f"Status: {response.status}")
    if response.video_url:
        print(f"Video URL: {response.video_url}")
    if response.error_message:
        print(f"Error: {response.error_message}")


if __name__ == "__main__":
    main()
