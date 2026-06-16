"""Cloud storage client for video and image storage"""

import os
from typing import Optional, List
from pathlib import Path
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract storage backend"""

    @abstractmethod
    def upload(self, local_path: str, remote_path: str) -> bool:
        """Upload file to storage"""
        pass

    @abstractmethod
    def download(self, remote_path: str, local_path: str) -> bool:
        """Download file from storage"""
        pass

    @abstractmethod
    def delete(self, remote_path: str) -> bool:
        """Delete file from storage"""
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in storage"""
        pass


class LocalStorageBackend(StorageBackend):
    """Local file storage backend"""

    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload(self, local_path: str, remote_path: str) -> bool:
        """
        Copy file to local storage.

        Args:
            local_path: Source file path
            remote_path: Destination file path in storage

        Returns:
            True if successful
        """
        try:
            src = Path(local_path)
            if not src.exists():
                return False

            dst = self.base_path / remote_path
            dst.parent.mkdir(parents=True, exist_ok=True)

            with open(src, "rb") as f_in:
                with open(dst, "wb") as f_out:
                    f_out.write(f_in.read())
            return True
        except Exception as e:
            print(f"Upload error: {e}")
            return False

    def download(self, remote_path: str, local_path: str) -> bool:
        """
        Copy file from local storage.

        Args:
            remote_path: File path in storage
            local_path: Destination file path

        Returns:
            True if successful
        """
        try:
            src = self.base_path / remote_path
            if not src.exists():
                return False

            dst = Path(local_path)
            dst.parent.mkdir(parents=True, exist_ok=True)

            with open(src, "rb") as f_in:
                with open(dst, "wb") as f_out:
                    f_out.write(f_in.read())
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False

    def delete(self, remote_path: str) -> bool:
        """
        Delete file from local storage.

        Args:
            remote_path: File path in storage

        Returns:
            True if successful
        """
        try:
            file_path = self.base_path / remote_path
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in local storage.

        Args:
            prefix: Optional path prefix filter

        Returns:
            List of file paths
        """
        try:
            search_path = self.base_path / prefix if prefix else self.base_path
            if not search_path.exists():
                return []

            return [str(p.relative_to(self.base_path)) for p in search_path.rglob("*") if p.is_file()]
        except Exception as e:
            print(f"List files error: {e}")
            return []


class GCSStorageBackend(StorageBackend):
    """Google Cloud Storage backend"""

    def __init__(self, bucket_name: str, project_id: Optional[str] = None):
        try:
            from google.cloud import storage
            self.client = storage.Client(project=project_id)
            self.bucket = self.client.bucket(bucket_name)
        except ImportError:
            raise ImportError("google-cloud-storage not installed")

    def upload(self, local_path: str, remote_path: str) -> bool:
        """
        Upload file to GCS.

        Args:
            local_path: Local file path
            remote_path: GCS blob path

        Returns:
            True if successful
        """
        try:
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            return True
        except Exception as e:
            print(f"GCS upload error: {e}")
            return False

    def download(self, remote_path: str, local_path: str) -> bool:
        """
        Download file from GCS.

        Args:
            remote_path: GCS blob path
            local_path: Local destination path

        Returns:
            True if successful
        """
        try:
            blob = self.bucket.blob(remote_path)
            blob.download_to_filename(local_path)
            return True
        except Exception as e:
            print(f"GCS download error: {e}")
            return False

    def delete(self, remote_path: str) -> bool:
        """
        Delete file from GCS.

        Args:
            remote_path: GCS blob path

        Returns:
            True if successful
        """
        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"GCS delete error: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in GCS.

        Args:
            prefix: Optional prefix filter

        Returns:
            List of blob names
        """
        try:
            blobs = self.client.list_blobs(self.bucket, prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"GCS list error: {e}")
            return []


class StorageClient:
    """Universal storage client"""

    def __init__(self, storage_type: str = "local", **kwargs):
        """
        Initialize storage client.

        Args:
            storage_type: Type of storage (local, gcs, s3)
            **kwargs: Backend-specific arguments
        """
        if storage_type == "local":
            self.backend = LocalStorageBackend(kwargs.get("base_path", "./storage"))
        elif storage_type == "gcs":
            self.backend = GCSStorageBackend(
                bucket_name=kwargs.get("bucket_name"),
                project_id=kwargs.get("project_id")
            )
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

    def upload(self, local_path: str, remote_path: str) -> bool:
        """Upload file to storage"""
        return self.backend.upload(local_path, remote_path)

    def download(self, remote_path: str, local_path: str) -> bool:
        """Download file from storage"""
        return self.backend.download(remote_path, local_path)

    def delete(self, remote_path: str) -> bool:
        """Delete file from storage"""
        return self.backend.delete(remote_path)

    def list_files(self, prefix: str = "") -> List[str]:
        """List files in storage"""
        return self.backend.list_files(prefix)
