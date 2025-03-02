"""Integration with Microsoft's Markitdown document conversion library."""

import logging
import os
import tempfile
from typing import Any, Optional

from markitdown import MarkItDown

from app.services.document.parser_base import (
    DocumentParser,
    ParserRegistry,
    ParsingResult,
)

VALID_HEADING_LEVELS = 6


class MarkitdownParser(DocumentParser):
    """Document parser using Microsoft's Markitdown library."""

    _instance: Optional['MarkitdownParser'] = None

    @classmethod
    def get_instance(cls) -> 'MarkitdownParser':
        """Get or create a singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize Markitdown parser with configuration."""
        try:
            self.md = MarkItDown()
            logging.info('MarkitdownParser initialized with basic capabilities')
        except Exception as e:
            logging.error(f'Failed to initialize MarkItDown: {e}')
            self.md = None

    @classmethod
    def supported_mimetypes(cls) -> list[str]:
        """Return list of supported MIME types."""
        return [
            # Documents
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            # Images
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/tiff',
            # Text formats
            'text/plain',
            'text/csv',
            'application/json',
            'text/html',
            # Archives
            'application/zip',
            'application/x-zip-compressed',
        ]

    async def parse(self, content: bytes, filename: str | None = None) -> ParsingResult:
        """
        Parse document content using Markitdown.

        Args:
            content: Binary content of the document
            filename: Optional filename for reference

        Returns:
            ParsingResult containing extracted information
        """
        if self.md is None:
            return ParsingResult(
                text='', error='Markitdown library not properly initialized'
            )

        temp_path = None
        try:
            # Create a file extension for temp file
            extension = ''
            if filename:
                extension = os.path.splitext(filename)[1]

            # Markitdown works with files, create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp:
                temp.write(content)
                temp_path = temp.name

            # Process with Markitdown
            result = self.md.convert(temp_path)

            # Extract text content
            text_content = result.text_content or ''

            # Extract available metadata
            metadata = self._extract_metadata(result)

            # Extract structure (based on available information)
            structure = self._extract_structure(result, text_content)

            # Determine page count
            pages = metadata.get('page_count', 1)

            # Log processing result
            file_type = metadata.get('source_format', 'unknown')
            logging.info(f'Successfully parsed {file_type} document with {pages} pages')

            return ParsingResult(
                text=text_content, metadata=metadata, pages=pages, structure=structure
            )
        except Exception as e:
            logging.error(f'Markitdown parsing failed: {e!s}')
            return ParsingResult(text='', error=f'Markitdown parsing failed: {e!s}')
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logging.warning(f'Failed to delete temp file {temp_path}: {e}')

    def _extract_metadata(self, result) -> dict[str, Any]:
        """Extract metadata from Markitdown result."""
        metadata = {}

        # Add standard metadata if available
        if hasattr(result, 'metadata') and result.metadata:
            for key, value in result.metadata.items():
                if value:  # Only add non-empty values
                    metadata[key] = value

        # Add source format
        if hasattr(result, 'source_format'):
            metadata['source_format'] = result.source_format

        # Add word count if available
        if hasattr(result, 'word_count'):
            metadata['word_count'] = result.word_count

        # Check for tables
        if hasattr(result, 'tables'):
            metadata['has_tables'] = len(result.tables) > 0
            metadata['table_count'] = len(result.tables)

        return metadata

    def _extract_structure(self, result, text_content: str) -> dict[str, Any]:
        """Extract document structure from Markitdown result."""
        structure = {}

        # Extract headings from markdown text
        structure['headings'] = self._extract_headings(text_content)

        # Add tables if available
        if hasattr(result, 'tables') and result.tables:
            structure['tables'] = result.tables

        # Add images if available
        if hasattr(result, 'images') and result.images:
            structure['has_images'] = True
            structure['image_count'] = len(result.images)

        return structure

    def _extract_headings(self, markdown_text: str) -> list[dict[str, Any]]:
        """Extract headings from markdown text."""
        headings = []
        for line in markdown_text.split('\n'):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= VALID_HEADING_LEVELS:  # Valid Markdown heading levels
                    text = line.lstrip('# ')
                    headings.append({'level': level, 'text': text})
        return headings


# Register the parser
ParserRegistry.register(MarkitdownParser)

# TODO: Future enhancements
# 1. Integrate with Azure Document Intelligence for advanced parsing
# 2. Add support for speech transcription of audio files
# 3. Implement LLM-based image description capabilities
