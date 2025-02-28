from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    """Abstract base class for storage providers."""

    @abstractmethod
    async def save_file(
        self, file: BinaryIO, path: str, content_type: str | None = None
    ) -> str:
        """Save file to storage and return the file path/URL."""
        pass

    @abstractmethod
    async def get_file(self, path: str) -> tuple[BinaryIO, str]:
        """Retrieve file from storage."""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Delete file from storage."""
        pass
