"""FastAPI application setup"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
import logging

from src.config import get_settings
from src.api.routes import (
    character_router, scene_router, video_router, job_router, health_router
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Veo 3 Character Video Generator",
    description="8K Video Generator with Character Consistency & Frame Matching",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP compression
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Include routers
app.include_router(health_router)
app.include_router(character_router)
app.include_router(scene_router)
app.include_router(video_router)
app.include_router(job_router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting Veo 3 Video Generator API")
    settings.ensure_directories()

    # Validate API key
    if not settings.validate_api_key():
        logger.warning("Google API key not configured - video generation will not work")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down Veo 3 Video Generator API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        workers=settings.api_workers if not settings.api_debug else 1
    )
