"""API routes for Veo 3 Video Generator"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Optional
import os
from datetime import datetime

from .schemas import (
    CharacterCreate, CharacterResponse, SceneCreate, SceneUpdate, SceneResponse,
    VideoGenerationRequest, VideoGenerationResponse, BatchVideoRequest,
    FrameMatchRequest, FrameMatchResponse, ConsistencyCheckRequest, ConsistencyScore,
    JobStatusResponse
)
from src.character.character_manager import CharacterManager
from src.character.consistency_engine import ConsistencyEngine
from src.scene.scene_manager import SceneManager
from src.scene.prompt_builder import PromptBuilder
from src.video.veo3_client import Veo3Client, VideoGenerationRequest as VeoRequest
from src.video.frame_extractor import FrameExtractor
from src.video.frame_matcher import FrameMatcher
from src.config import get_settings

# Initialize components
settings = get_settings()
character_manager = CharacterManager()
consistency_engine = ConsistencyEngine(threshold=settings.character_consistency_threshold)
scene_manager = SceneManager()
prompt_builder = PromptBuilder()
veo3_client = Veo3Client(api_key=settings.google_api_key, model=settings.veo3_model)
frame_extractor = FrameExtractor()
frame_matcher = FrameMatcher()

# Initialize routers
character_router = APIRouter(prefix="/api/v1/characters", tags=["Characters"])
scene_router = APIRouter(prefix="/api/v1/scenes", tags=["Scenes"])
video_router = APIRouter(prefix="/api/v1/videos", tags=["Videos"])
job_router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


# Character Routes
@character_router.post("", response_model=CharacterResponse)
async def create_character(character: CharacterCreate):
    """Create a new character with reference images"""
    try:
        char = character_manager.add_character(
            id=character.id,
            name=character.name,
            description=character.description,
            reference_images=character.reference_images
        )
        return CharacterResponse(
            id=char.id,
            name=char.name,
            description=char.description,
            reference_images=char.reference_images,
            created_at=char.created_at,
            updated_at=char.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@character_router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str):
    """Get character by ID"""
    char = character_manager.get_character(character_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    return CharacterResponse(
        id=char.id,
        name=char.name,
        description=char.description,
        reference_images=char.reference_images,
        created_at=char.created_at,
        updated_at=char.updated_at
    )


@character_router.get("", response_model=List[CharacterResponse])
async def list_characters():
    """List all characters"""
    characters = character_manager.list_characters()
    return [
        CharacterResponse(
            id=char.id,
            name=char.name,
            description=char.description,
            reference_images=char.reference_images,
            created_at=char.created_at,
            updated_at=char.updated_at
        )
        for char in characters
    ]


@character_router.delete("/{character_id}")
async def delete_character(character_id: str):
    """Delete a character"""
    if character_manager.delete_character(character_id):
        return {"message": "Character deleted successfully"}
    raise HTTPException(status_code=404, detail="Character not found")


# Scene Routes
@scene_router.post("", response_model=SceneResponse)
async def create_scene(scene: SceneCreate):
    """Create a new scene"""
    try:
        created_scene = scene_manager.add_scene(
            scene_id=scene.id,
            name=scene.name,
            description=scene.description,
            prompt=scene.prompt,
            character_id=scene.character_id,
            duration=scene.duration,
            reference_image=scene.reference_image
        )
        return SceneResponse(
            id=created_scene.id,
            name=created_scene.name,
            description=created_scene.description,
            prompt=created_scene.prompt,
            character_id=created_scene.character_id,
            duration=created_scene.duration,
            sequence_index=created_scene.sequence_index,
            created_at=created_scene.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@scene_router.get("/{scene_id}", response_model=SceneResponse)
async def get_scene(scene_id: str):
    """Get scene by ID"""
    scene = scene_manager.get_scene(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    return SceneResponse(
        id=scene.id,
        name=scene.name,
        description=scene.description,
        prompt=scene.prompt,
        character_id=scene.character_id,
        duration=scene.duration,
        sequence_index=scene.sequence_index,
        created_at=scene.created_at
    )


@scene_router.get("", response_model=List[SceneResponse])
async def list_scenes():
    """List all scenes in order"""
    scenes = scene_manager.get_scene_sequence()
    return [
        SceneResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            prompt=s.prompt,
            character_id=s.character_id,
            duration=s.duration,
            sequence_index=s.sequence_index,
            created_at=s.created_at
        )
        for s in scenes
    ]


@scene_router.put("/{scene_id}", response_model=SceneResponse)
async def update_scene(scene_id: str, scene_update: SceneUpdate):
    """Update scene"""
    updated_scene = scene_manager.update_scene(scene_id, **scene_update.dict(exclude_unset=True))
    if not updated_scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    return SceneResponse(
        id=updated_scene.id,
        name=updated_scene.name,
        description=updated_scene.description,
        prompt=updated_scene.prompt,
        character_id=updated_scene.character_id,
        duration=updated_scene.duration,
        sequence_index=updated_scene.sequence_index,
        created_at=updated_scene.created_at
    )


@scene_router.delete("/{scene_id}")
async def delete_scene(scene_id: str):
    """Delete a scene"""
    if scene_manager.delete_scene(scene_id):
        return {"message": "Scene deleted successfully"}
    raise HTTPException(status_code=404, detail="Scene not found")


# Video Generation Routes
@video_router.post("/text-to-video", response_model=VideoGenerationResponse)
async def generate_text_to_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Generate video from text prompt"""
    try:
        veo_request = VeoRequest(
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.resolution,
            fps=request.fps,
            aspect_ratio=request.aspect_ratio,
            model=request.model,
            quality=request.quality
        )
        response = veo3_client.generate_text_to_video(veo_request)
        return VideoGenerationResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@video_router.post("/batch", response_model=dict)
async def generate_batch_video(request: BatchVideoRequest, background_tasks: BackgroundTasks):
    """Generate multiple videos in sequence with frame matching"""
    try:
        character = character_manager.get_character(request.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        scenes = [scene_manager.get_scene(sid) for sid in request.scene_ids]
        if not all(scenes):
            raise HTTPException(status_code=404, detail="One or more scenes not found")

        return {
            "message": "Batch video generation started",
            "character_id": request.character_id,
            "scene_count": len(scenes),
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Frame Matching Routes
@video_router.post("/match-frames", response_model=FrameMatchResponse)
async def match_frames(request: FrameMatchRequest):
    """Match two frames for transition quality"""
    try:
        from src.video.frame_extractor import FrameData
        import cv2

        ref_frame = cv2.imread(request.ref_frame_path)
        curr_frame = cv2.imread(request.curr_frame_path)

        if ref_frame is None or curr_frame is None:
            raise HTTPException(status_code=400, detail="Invalid frame paths")

        ref_data = FrameData(0, 0, ref_frame, ref_frame.shape[0], ref_frame.shape[1], datetime.utcnow().isoformat())
        curr_data = FrameData(0, 0, curr_frame, curr_frame.shape[0], curr_frame.shape[1], datetime.utcnow().isoformat())

        match = frame_matcher.match_frames(ref_data, curr_data)

        quality = "excellent" if match.similarity_score > 0.9 else \
                  "good" if match.similarity_score > 0.75 else \
                  "fair" if match.similarity_score > 0.5 else "poor"

        return FrameMatchResponse(
            similarity_score=match.similarity_score,
            keypoint_matches=match.keypoint_matches,
            feature_distance=match.feature_distance,
            match_quality=quality
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Job Status Routes
@job_router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status"""
    try:
        status = veo3_client.get_job_status(job_id)
        return JobStatusResponse(
            job_id=job_id,
            status=status.get("status", "unknown"),
            progress=status.get("progress", 0),
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Health Check
health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@health_router.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "veo3_model": settings.veo3_model,
        "video_resolution": settings.video_default_resolution,
        "video_fps": settings.video_default_resolution,
        "character_consistency_threshold": settings.character_consistency_threshold
    }
