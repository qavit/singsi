"""Image document parser implementation with OCR capabilities."""

import io
from typing import Any

import pytesseract
from PIL import Image

from app.services.document.parser_base import (
    DocumentParser,
    ParserRegistry,
    ParsingResult,
)


class ImageParser(DocumentParser):
    """Parser for image files with OCR capabilities."""

    @classmethod
    def supported_mimetypes(cls) -> list[str]:
        """Return list of supported MIME types."""
        return [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/tiff',
            'image/bmp',
            'image/webp',
        ]

    MIN_TEXT_LENGTH = 20
    DOCUMENT_TEXT_THRESHOLD = 100

    async def parse(self, content: bytes, filename: str | None = None) -> ParsingResult:
        """Parse image content with OCR."""
        try:
            # Open image from bytes
            img = Image.open(io.BytesIO(content))

            # Extract basic image metadata
            metadata = self._extract_metadata(img)

            # Perform OCR
            # TODO: Improve OCR quality for educational materials
            # - Add support for mathematical notation
            # - Implement detection of tables and forms
            # - Consider custom OCR training for specific document types
            text = pytesseract.image_to_string(img)

            # If OCR failed to extract meaningful text
            if not text or len(text.strip()) < self.MIN_TEXT_LENGTH:
                return ParsingResult(
                    text='[Image with limited or no extractable text]',
                    metadata=metadata,
                    error='OCR extracted limited text; '
                    'consider using AI image description',
                )

            return ParsingResult(
                text=text,
                metadata=metadata,
                structure={
                    'image_type': 'document'
                    if len(text) > self.DOCUMENT_TEXT_THRESHOLD
                    else 'photo'
                },
            )

        except Exception as e:
            return ParsingResult(text='', error=f'Image parsing failed: {e!s}')

    def _extract_metadata(self, img: Image.Image) -> dict[str, Any]:
        """Extract metadata from image."""
        return {
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'mode': img.mode,
            'dpi': img.info.get('dpi'),
        }


# Register the parser
ParserRegistry.register(ImageParser)
