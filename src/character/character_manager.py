"""Character reference and metadata management"""

import os
import json
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


@dataclass
class Character:
    """Character metadata and reference data"""
    id: str
    name: str
    description: str
    reference_images: List[str]  # File paths
    embeddings: Optional[List[np.ndarray]] = None
    pose_data: Optional[Dict] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.utcnow().isoformat()


class CharacterManager:
    """Manages character references and consistency data"""

    def __init__(self, cache_dir: str = "./cache/characters"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.characters: Dict[str, Character] = {}
        self._load_cache()

    def add_character(self, id: str, name: str, description: str,
                     reference_images: List[str]) -> Character:
        """Add a new character with reference images"""
        # Validate reference images
        validated_images = []
        for img_path in reference_images:
            if os.path.exists(img_path):
                validated_images.append(img_path)
            else:
                raise FileNotFoundError(f"Reference image not found: {img_path}")

        character = Character(
            id=id,
            name=name,
            description=description,
            reference_images=validated_images
        )
        self.characters[id] = character
        self._save_cache()
        return character

    def get_character(self, character_id: str) -> Optional[Character]:
        """Retrieve character by ID"""
        return self.characters.get(character_id)

    def list_characters(self) -> List[Character]:
        """List all characters"""
        return list(self.characters.values())

    def delete_character(self, character_id: str) -> bool:
        """Delete a character"""
        if character_id in self.characters:
            del self.characters[character_id]
            self._save_cache()
            return True
        return False

    def update_embeddings(self, character_id: str, embeddings: List[np.ndarray]) -> None:
        """Update character embeddings"""
        if character_id in self.characters:
            self.characters[character_id].embeddings = embeddings
            self.characters[character_id].updated_at = datetime.utcnow().isoformat()
            self._save_cache()

    def update_pose_data(self, character_id: str, pose_data: Dict) -> None:
        """Update character pose data"""
        if character_id in self.characters:
            self.characters[character_id].pose_data = pose_data
            self.characters[character_id].updated_at = datetime.utcnow().isoformat()
            self._save_cache()

    def get_character_hash(self, character_id: str) -> Optional[str]:
        """Generate hash of character reference images for consistency checking"""
        character = self.get_character(character_id)
        if not character:
            return None

        hasher = hashlib.md5()
        for img_path in character.reference_images:
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    hasher.update(f.read())

        return hasher.hexdigest()

    def extract_character_features(self, character_id: str) -> Dict:
        """Extract visual features from character reference images"""
        character = self.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")

        features = {
            "id": character_id,
            "image_count": len(character.reference_images),
            "dimensions": [],
            "color_profiles": []
        }

        for img_path in character.reference_images:
            img = cv2.imread(img_path)
            if img is not None:
                features["dimensions"].append({"height": img.shape[0], "width": img.shape[1]})
                # Calculate average color
                avg_color = cv2.mean(img)[:3]
                features["color_profiles"].append({"bgr": list(avg_color)})

        return features

    def _save_cache(self) -> None:
        """Save character cache to disk"""
        cache_file = self.cache_dir / "characters.json"
        data = {}
        for char_id, char in self.characters.items():
            char_dict = asdict(char)
            char_dict["embeddings"] = None  # Don't serialize embeddings
            data[char_id] = char_dict

        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_cache(self) -> None:
        """Load character cache from disk"""
        cache_file = self.cache_dir / "characters.json"
        if cache_file.exists():
            with open(cache_file, "r") as f:
                data = json.load(f)
                for char_id, char_dict in data.items():
                    self.characters[char_id] = Character(**char_dict)
