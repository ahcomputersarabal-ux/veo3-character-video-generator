"""API schemas and request/response models"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Character Models
class CharacterCreate(BaseModel):
    """Create character request"""
    id: str
    name: str
    description: str
    reference_images: List[str]


class CharacterResponse(BaseModel):
    """Character response"""
    id: str
    name: str
    description: str
    reference_images: List[str]
    created_at: str
    updated_at: str


# Scene Models
class SceneCreate(BaseModel):
    """Create scene request"""
    id: str
    name: str
    description: str
    prompt: str
    character_id: Optional[str] = None
    duration: int = 6
    reference_image: Optional[str] = None


class SceneUpdate(BaseModel):
    """Update scene request"""
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    duration: Optional[int] = None


class SceneResponse(BaseModel):
    """Scene response"""
    id: str
    name: str
    description: str
    prompt: str
    character_id: Optional[str]
    duration: int
    sequence_index: int
    created_at: str


# Video Generation Models
class VideoGenerationRequest(BaseModel):
    """Video generation request"""
    prompt: str
    duration: int = Field(default=6, ge=4, le=8)
    resolution: str = "4K"
    fps: int = 24
    aspect_ratio: str = "16:9"
    model: str = "veo3-fast"
    quality: str = "high"


class VideoGenerationResponse(BaseModel):
    """Video generation response"""
    job_id: str
    status: str
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    metadata: dict


class BatchVideoRequest(BaseModel):
    """Batch video generation request"""
    character_id: str
    scene_ids: List[str]
    match_frames: bool = True
    auto_transition: bool = True


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    progress: float
    created_at: str
    updated_at: str
    result: Optional[VideoGenerationResponse] = None


# Frame Matching Models
class FrameMatchRequest(BaseModel):
    """Frame matching request"""
    ref_frame_path: str
    curr_frame_path: str


class FrameMatchResponse(BaseModel):
    """Frame matching response"""
    similarity_score: float
    keypoint_matches: int
    feature_distance: float
    match_quality: str


# Consistency Models
class ConsistencyCheckRequest(BaseModel):
    """Consistency check request"""
    character_id: str
    frame_path: str


class ConsistencyScore(BaseModel):
    """Consistency score response"""
    character_id: str
    score: float
    appearance_score: float
    pose_score: float
    lighting_score: float
    timestamp: str
