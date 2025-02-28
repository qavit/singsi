import mimetypes
from pathlib import Path
from typing import Any, BinaryIO

from app.models.document import Document, DocumentMetadata, DocumentType
from app.services.ai.factory import AIProviderFactory


class DocumentService:
    """Service for document processing and analysis."""

    def __init__(self) -> None:
        self.ai_provider = AIProviderFactory.create('openai')

    def _detect_document_type(self, filename: str, content_type: str) -> DocumentType:
        """Detect document type from filename and content type."""
        ext = Path(filename).suffix.lower()
        if ext in {'.pdf'}:
            return DocumentType.PDF
        elif ext in {'.doc', '.docx'}:
            return DocumentType.WORD
        elif ext in {'.txt'}:
            return DocumentType.TEXT
        elif ext in {'.md', '.markdown'}:
            return DocumentType.MARKDOWN
        elif content_type.startswith('image/'):
            return DocumentType.IMAGE
        else:
            raise ValueError(f'Unsupported file type: {filename} ({content_type})')

    async def process_document(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        """Process and analyze uploaded document."""
        content = file.read()
        content_type = (
            content_type
            or mimetypes.guess_type(filename)[0]
            or 'application/octet-stream'
        )

        # If metadata is not provided, use filename as title
        if metadata is None:
            metadata = {'title': filename}

        # Create document model
        doc = Document(
            filename=filename,
            content_type=content_type,
            file_size=len(content),
            type=self._detect_document_type(filename, content_type),
            metadata=DocumentMetadata(**metadata),
        )

        # Analyze document content
        doc.analysis_results = await self.ai_provider.analyze_document(
            content=content,
            filename=filename,
            content_type=content_type,
        )

        return doc


# Create singleton instance
document_service = DocumentService()
