"""Caching layer for video frames and embeddings"""

import os
import json
import pickle
from typing import Any, Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta


class Cache:
    """Local cache for frames, embeddings, and metadata"""

    def __init__(self, cache_dir: str = "./cache", ttl_hours: int = 24):
        """
        Initialize cache.

        Args:
            cache_dir: Cache directory path
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()

    def set(self, key: str, value: Any, expire_hours: Optional[int] = None) -> bool:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be serializable)
            expire_hours: Optional custom expiration in hours

        Returns:
            True if successful
        """
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            with open(cache_file, "wb") as f:
                pickle.dump(value, f)

            expiry = datetime.utcnow() + timedelta(hours=expire_hours or self.ttl.days * 24 + self.ttl.seconds // 3600)
            self.metadata[key] = {
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": expiry.isoformat(),
                "file_path": str(cache_file)
            }
            self._save_metadata()
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        try:
            if key not in self.metadata:
                return None

            meta = self.metadata[key]
            expires_at = datetime.fromisoformat(meta["expires_at"])

            if datetime.utcnow() > expires_at:
                self.delete(key)
                return None

            cache_file = Path(meta["file_path"])
            if not cache_file.exists():
                return None

            with open(cache_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Delete cache entry.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        try:
            if key in self.metadata:
                cache_file = Path(self.metadata[key]["file_path"])
                if cache_file.exists():
                    cache_file.unlink()
                del self.metadata[key]
                self._save_metadata()
                return True
            return False
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful
        """
        try:
            for key in list(self.metadata.keys()):
                self.delete(key)
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        removed = 0
        current_time = datetime.utcnow()

        for key in list(self.metadata.keys()):
            meta = self.metadata[key]
            expires_at = datetime.fromisoformat(meta["expires_at"])
            if current_time > expires_at:
                self.delete(key)
                removed += 1

        return removed

    def get_cache_size(self) -> int:
        """
        Get total cache size in bytes.

        Returns:
            Total size
        """
        total_size = 0
        for cache_file in self.cache_dir.glob("*.pkl"):
            total_size += cache_file.stat().st_size
        return total_size

    def _load_metadata(self) -> Dict:
        """
        Load cache metadata from file.

        Returns:
            Metadata dictionary
        """
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_metadata(self) -> None:
        """
        Save cache metadata to file.
        """
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Metadata save error: {e}")
