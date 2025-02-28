import mimetypes
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile

from app.core.config import settings
from app.services.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider."""

    def __init__(self) -> None:
        self.root = Path(settings.STORAGE_ROOT)
        self.root.mkdir(parents=True, exist_ok=True)

    def _get_storage_path(self, filename: str) -> Path:
        """Generate storage path based on date and filename."""
        date_path = datetime.now().strftime('%Y/%m/%d')
        storage_path = self.root / date_path
        storage_path.mkdir(parents=True, exist_ok=True)
        return storage_path / filename

    async def save_file(
        self, file: BinaryIO, path: str, content_type: str | None = None
    ) -> str:
        """Save file to local storage."""
        storage_path = self._get_storage_path(path)

        if isinstance(file, UploadFile):
            async with file.file as f:
                content = await f.read()
        else:
            # If file is already read, seek to start
            if hasattr(file, 'seek'):
                file.seek(0)
            content = file.read()

        with storage_path.open('wb') as f:
            f.write(content)

        return str(storage_path.relative_to(self.root))

    async def get_file(self, path: str) -> tuple[BinaryIO, str]:
        """Retrieve file from local storage."""
        file_path = self.root / path
        if not file_path.exists():
            raise FileNotFoundError(f'File not found: {path}')

        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

        return file_path.open('rb'), content_type

    async def delete_file(self, path: str) -> bool:
        """Delete file from local storage."""
        try:
            file_path = self.root / path
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False


# Create singleton instance
storage_provider = LocalStorageProvider()
