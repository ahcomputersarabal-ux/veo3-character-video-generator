"""Scene management for multi-segment video generation"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Scene:
    """Represents a single scene/segment in a video sequence"""
    id: str
    name: str
    description: str
    prompt: str
    character_id: Optional[str] = None
    duration: int = 6  # seconds
    sequence_index: int = 0
    reference_image: Optional[str] = None
    last_frame_file: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict = field(default_factory=dict)


class SceneManager:
    """Manages scene sequences for video generation"""

    def __init__(self, cache_dir: str = "./cache/scenes"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.scenes: Dict[str, Scene] = {}
        self.scene_sequence: List[str] = []  # Ordered list of scene IDs

    def add_scene(self, scene_id: str, name: str, description: str, prompt: str,
                 character_id: Optional[str] = None, duration: int = 6,
                 reference_image: Optional[str] = None) -> Scene:
        """
        Add a new scene to the manager.

        Args:
            scene_id: Unique scene identifier
            name: Scene name
            description: Scene description
            prompt: Prompt for video generation
            character_id: Associated character ID
            duration: Scene duration in seconds
            reference_image: Optional reference image path

        Returns:
            Created Scene object
        """
        scene = Scene(
            id=scene_id,
            name=name,
            description=description,
            prompt=prompt,
            character_id=character_id,
            duration=duration,
            sequence_index=len(self.scene_sequence),
            reference_image=reference_image
        )
        self.scenes[scene_id] = scene
        self.scene_sequence.append(scene_id)
        self._save_cache()
        return scene

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """Get scene by ID"""
        return self.scenes.get(scene_id)

    def get_scene_sequence(self) -> List[Scene]:
        """Get scenes in order"""
        return [self.scenes[sid] for sid in self.scene_sequence if sid in self.scenes]

    def update_scene(self, scene_id: str, **kwargs) -> Optional[Scene]:
        """Update scene properties"""
        if scene_id not in self.scenes:
            return None

        scene = self.scenes[scene_id]
        for key, value in kwargs.items():
            if hasattr(scene, key):
                setattr(scene, key, value)

        self._save_cache()
        return scene

    def update_last_frame(self, scene_id: str, frame_file: str) -> bool:
        """Update last frame file for a scene"""
        if scene_id not in self.scenes:
            return False

        self.scenes[scene_id].last_frame_file = frame_file
        self._save_cache()
        return True

    def delete_scene(self, scene_id: str) -> bool:
        """Delete a scene"""
        if scene_id not in self.scenes:
            return False

        del self.scenes[scene_id]
        if scene_id in self.scene_sequence:
            self.scene_sequence.remove(scene_id)

        self._save_cache()
        return True

    def reorder_scenes(self, scene_order: List[str]) -> bool:
        """
        Reorder scenes in sequence.

        Args:
            scene_order: List of scene IDs in new order

        Returns:
            True if successful
        """
        if set(scene_order) != set(self.scene_sequence):
            return False

        self.scene_sequence = scene_order
        for idx, scene_id in enumerate(self.scene_sequence):
            self.scenes[scene_id].sequence_index = idx

        self._save_cache()
        return True

    def get_scene_count(self) -> int:
        """Get number of scenes"""
        return len(self.scene_sequence)

    def _save_cache(self) -> None:
        """Save scenes to cache file"""
        cache_file = self.cache_dir / "scenes.json"
        data = {
            "scene_sequence": self.scene_sequence,
            "scenes": {}
        }
        for sid, scene in self.scenes.items():
            data["scenes"][sid] = {
                "id": scene.id,
                "name": scene.name,
                "description": scene.description,
                "prompt": scene.prompt,
                "character_id": scene.character_id,
                "duration": scene.duration,
                "sequence_index": scene.sequence_index,
                "reference_image": scene.reference_image,
                "last_frame_file": scene.last_frame_file,
                "created_at": scene.created_at,
                "metadata": scene.metadata
            }

        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_cache(self) -> None:
        """Load scenes from cache file"""
        cache_file = self.cache_dir / "scenes.json"
        if not cache_file.exists():
            return

        with open(cache_file, "r") as f:
            data = json.load(f)

        self.scene_sequence = data.get("scene_sequence", [])
        for sid, scene_data in data.get("scenes", {}).items():
            self.scenes[sid] = Scene(**scene_data)
