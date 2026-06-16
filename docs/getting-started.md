# Veo 3 Character Video Generator - Getting Started

## Installation

### Prerequisites
- Python 3.9+
- Google Cloud Account with Veo 3 API access
- Git

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/ahcomputersarabal-ux/veo3-character-video-generator.git
cd veo3-character-video-generator
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

## Running the API Server

```bash
uvicorn src.api.app:app --reload
```

API will be available at: `http://localhost:8000`

### API Endpoints

**Swagger Documentation:** http://localhost:8000/docs

#### Characters
- `POST /api/v1/characters` - Create character
- `GET /api/v1/characters` - List characters
- `GET /api/v1/characters/{id}` - Get character
- `DELETE /api/v1/characters/{id}` - Delete character

#### Scenes
- `POST /api/v1/scenes` - Create scene
- `GET /api/v1/scenes` - List scenes
- `GET /api/v1/scenes/{id}` - Get scene
- `PUT /api/v1/scenes/{id}` - Update scene
- `DELETE /api/v1/scenes/{id}` - Delete scene

#### Video Generation
- `POST /api/v1/videos/text-to-video` - Generate from text
- `POST /api/v1/videos/batch` - Batch generation
- `POST /api/v1/videos/match-frames` - Match frames

## Running Examples

### Example 1: Basic Text-to-Video
```bash
python examples/basic_text_to_video.py
```

### Example 2: Character Consistency
```bash
python examples/character_consistency_demo.py
```

### Example 3: Scene Sequencing
```bash
python examples/scene_sequence_demo.py
```

## Docker Deployment

### Build and Run
```bash
docker-compose up --build
```

### Environment Variables
Create a `.env` file with:
```
GOOGLE_API_KEY=your_api_key
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_CLOUD_BUCKET=your_bucket_name
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_character_manager.py
```

## API Usage Examples

### Create a Character
```bash
curl -X POST http://localhost:8000/api/v1/characters \
  -H "Content-Type: application/json" \
  -d '{
    "id": "protagonist",
    "name": "Emma",
    "description": "Woman with long dark hair",
    "reference_images": []
  }'
```

### Create a Scene
```bash
curl -X POST http://localhost:8000/api/v1/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "scene_01",
    "name": "Forest Walk",
    "description": "Character walking through forest",
    "prompt": "A woman walking through a lush forest at sunset",
    "character_id": "protagonist",
    "duration": 6
  }'
```

### Generate Video
```bash
curl -X POST http://localhost:8000/api/v1/videos/text-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A woman with long dark hair walking through forest",
    "duration": 6,
    "resolution": "4K",
    "model": "veo3-fast",
    "quality": "high"
  }'
```

## Configuration

Edit `config.yaml` to customize:
- Video resolution and duration
- Character consistency thresholds
- Frame matching parameters
- Storage settings
- API settings

## Troubleshooting

### API Key Issues
- Ensure `GOOGLE_API_KEY` is set in `.env`
- Check key validity at Google Cloud Console
- Verify Veo 3 API is enabled in your project

### Video Generation Fails
- Check internet connection
- Verify API quota limits
- Check logs for detailed error messages

### Frame Matching Issues
- Ensure frames are in valid video format
- Check frame dimensions match
- Verify sufficient keypoints detected

## Next Steps

1. **Integrate with UI**: Build a web interface using React/Vue
2. **Add webhooks**: Implement async notifications
3. **Scale horizontally**: Deploy with Kubernetes
4. **Advanced features**: Add more transition types, effects, audio sync

## Support

- **Issues**: [GitHub Issues](https://github.com/ahcomputersarabal-ux/veo3-character-video-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ahcomputersarabal-ux/veo3-character-video-generator/discussions)
