"""Base definitions for document parsing system."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class ParsingResult:
    """Container for document parsing results."""

    def __init__(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        pages: int = 1,
        structure: dict[str, Any] | None = None,
        optional_data: dict[str, Any] | None = None,
    ):
        error = optional_data.get('error') if optional_data else None
        tables = optional_data.get('tables') if optional_data else None
        images = optional_data.get('images') if optional_data else None
        audio_transcription = (
            optional_data.get('audio_transcription') if optional_data else None
        )
        """
        Initialize parsing result.

        Args:
            text: Extracted text content
            metadata: Document metadata (author, creation date, etc.)
            pages: Number of pages or sections
            structure: Document structure (headings, paragraphs, etc.)
            error: Any error that occurred during parsing
        """
        self.text = text
        self.metadata = metadata or {}
        self.pages = pages
        self.structure = structure or {}
        self.error = error
        self.tables = tables or []
        self.images = images or []
        self.audio_transcription = audio_transcription

    @property
    def success(self) -> bool:
        """Check if parsing was successful."""
        return self.error is None

    def to_dict(self) -> dict[str, Any]:
        """Convert parsing result to a dictionary."""
        result = {
            'text': self.text,
            'metadata': self.metadata,
            'pages': self.pages,
            'structure': self.structure,
            'success': self.success,
            'error': self.error,
        }

        # Add optional fields if present
        if self.tables:
            result['tables'] = self.tables
        if self.images:
            result['images'] = self.images
        if self.audio_transcription:
            result['audio_transcription'] = self.audio_transcription

        return result


class DocumentParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    async def parse(self, content: bytes, filename: str | None = None) -> ParsingResult:
        """
        Parse document content.

        Args:
            content: Binary content of the document
            filename: Optional filename for reference

        Returns:
            ParsingResult containing extracted information
        """
        pass

    @classmethod
    @abstractmethod
    def supported_mimetypes(cls) -> list[str]:
        """Return list of supported MIME types."""
        pass


class ParserRegistry:
    """Registry for document parsers."""

    _parsers: ClassVar[dict[str, type[DocumentParser]]] = {}

    @classmethod
    def register(cls, parser_class: type[DocumentParser]) -> None:
        """Register a parser class for its supported MIME types."""
        for mimetype in parser_class.supported_mimetypes():
            cls._parsers[mimetype] = parser_class

    @classmethod
    def get_parser(cls, mimetype: str) -> type[DocumentParser] | None:
        """Get parser class for the given MIME type."""
        return cls._parsers.get(mimetype)

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of all supported MIME types."""
        return list(cls._parsers.keys())
