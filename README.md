# Veo 3 Character Video Generator

**8K Video Generator with Character Consistency & Smooth Frame Matching**

A professional-grade video generation system powered by Google's Veo 3.1 API, featuring advanced character consistency tracking, intelligent frame matching, and seamless scene transitions.

## 🎬 Features

✅ **Text-to-Video & Image-to-Video Generation**  
✅ **Character Consistency Engine** - Maintain visual coherence across scenes  
✅ **Smart Frame Matching** - Extract and match last frames for smooth joints  
✅ **4K/8K Output Support** - Generate in up to 4K resolution  
✅ **Synchronized Audio** - Native dialogue, SFX, and ambiance  
✅ **Batch Processing** - Generate multiple scenes in sequence  
✅ **Real-time Status Tracking** - WebSocket-based job monitoring  
✅ **Cloud Storage Integration** - Google Cloud Storage support  
✅ **REST API** - Full API with comprehensive endpoints  

## 📋 Architecture

```
veo3-character-video-generator/
├── src/
│   ├── character/
│   │   ├── __init__.py
│   │   ├── character_manager.py      # Character reference management
│   │   ├── consistency_engine.py     # Visual consistency tracking
│   │   └── pose_detector.py          # Pose estimation & tracking
│   ├── video/
│   │   ├── __init__.py
│   │   ├── frame_extractor.py        # Extract frames from videos
│   │   ├── frame_matcher.py          # Match & blend frames for smooth transitions
│   │   └── veo3_client.py            # Veo 3 API client
│   ├── scene/
│   │   ├── __init__.py
│   │   ├── scene_manager.py          # Scene sequence management
│   │   ├── prompt_builder.py         # Intelligent prompt generation
│   │   └── transition_handler.py     # Smooth transition logic
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── cache.py                  # Caching layer
│   │   └── storage_client.py         # Cloud storage integration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py                    # FastAPI application
│   │   ├── routes.py                 # API endpoints
│   │   └── schemas.py                # Pydantic models
│   └── config.py                     # Configuration management
├── tests/
├── examples/
├── requirements.txt
├── .env.example
├── config.yaml
└── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Cloud Account with Veo 3 API access

### Installation

```bash
git clone https://github.com/ahcomputersarabal-ux/veo3-character-video-generator.git
cd veo3-character-video-generator
pip install -r requirements.txt
cp .env.example .env
# Add your Google API key to .env
```

### Run API

```bash
uvicorn src.api.app:app --reload
```

API available at: `http://localhost:8000`

## 📚 Documentation

- [Getting Started](docs/getting-started.md)
- [Character Consistency Guide](docs/character-consistency.md)
- [Frame Matching Reference](docs/frame-matching.md)
- [API Reference](docs/api-reference.md)

## 🤝 Contributing

Contributions welcome! Please create a feature branch and submit a PR.

## 📝 License

MIT License - see LICENSE file for details.
