import os
import shutil
from abc import ABC, abstractmethod
from typing import Union, Optional
from app.core.config import settings

class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: Union[bytes, str]) -> str:
        """Save data to key and return stored location/path."""
        pass

    @abstractmethod
    def save_atomic(self, key: str, data: Union[bytes, str]) -> str:
        """Atomically write data to key via staging file swap."""
        pass

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Return accessible URL or path for stored key."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete stored key."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in storage."""
        pass

    @abstractmethod
    def read(self, key: str) -> bytes:
        """Read bytes from storage."""
        pass


class LocalDiskStorage(StorageBackend):
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or settings.STORAGE_DIR)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        # Prevent directory traversal
        normalized_key = os.path.normpath(key).lstrip("/\\")
        return os.path.join(self.base_dir, normalized_key)

    def save(self, key: str, data: Union[bytes, str]) -> str:
        file_path = self._get_path(key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        mode = "wb" if isinstance(data, bytes) else "w"
        encoding = None if isinstance(data, bytes) else "utf-8"
        with open(file_path, mode, encoding=encoding) as f:
            f.write(data)
        return file_path

    def save_atomic(self, key: str, data: Union[bytes, str]) -> str:
        target_path = self._get_path(key)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        tmp_path = f"{target_path}.tmp_{os.getpid()}"
        
        mode = "wb" if isinstance(data, bytes) else "w"
        encoding = None if isinstance(data, bytes) else "utf-8"
        
        with open(tmp_path, mode, encoding=encoding) as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
            
        # Atomic rename/swap
        os.replace(tmp_path, target_path)
        return target_path

    def get_url(self, key: str) -> str:
        # In a real environment with static file serving, this returns /storage/key
        normalized_key = key.lstrip("/\\").replace("\\", "/")
        return f"/storage/{normalized_key}"

    def delete(self, key: str) -> bool:
        file_path = self._get_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def exists(self, key: str) -> bool:
        return os.path.exists(self._get_path(key))

    def read(self, key: str) -> bytes:
        file_path = self._get_path(key)
        with open(file_path, "rb") as f:
            return f.read()


# Global storage instance. To swap to R2Storage, change this single factory line!
def get_storage() -> StorageBackend:
    return LocalDiskStorage()
