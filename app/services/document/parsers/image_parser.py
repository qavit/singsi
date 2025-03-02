"""Image parser with OCR and basic image analysis capabilities."""

import io
import logging
from typing import Any

import pytesseract
from PIL import Image

from app.services.document.parser_base import (
    DocumentParser,
    ParserRegistry,
    ParsingResult,
)

# Configure Tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'


class ImageParser(DocumentParser):
    """Processes image files and extracts text content using OCR."""

    def __init__(self, lang: str = 'chi_tra+eng'):
        """
        Initialize the image parser.

        Args:
            lang: Tesseract language code, defaults to Traditional Chinese + English
                 Available options:
                 - 'eng': English
                 - 'chi_sim': Simplified Chinese
                 - 'chi_tra': Traditional Chinese
                 - 'chi_tra+eng': Traditional Chinese and English
                 - 'chi_sim+eng': Simplified Chinese and English
                 - 'jpn': Japanese
                 - 'kor': Korean
        """
        self.lang = lang
        self.logger = logging.getLogger(__name__)

    @classmethod
    def supported_mimetypes(cls) -> list[str]:
        """Return a list of supported MIME types."""
        return [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/tiff',
            'image/bmp',
        ]

    async def parse(self, content: bytes, filename: str | None = None) -> ParsingResult:
        """
        Parse image content.

        Args:
            content: Binary content of the image
            filename: Optional filename for reference

        Returns:
            ParsingResult containing extracted information
        """
        try:
            # Open image using PIL
            image = Image.open(io.BytesIO(content))

            # Preprocess image to improve OCR quality
            processed_image = self._preprocess_image(image)

            # Perform OCR using pytesseract
            text = pytesseract.image_to_string(processed_image, lang=self.lang)

            # Extract structured information (such as tables)
            tables = self._extract_tables(image)

            # Analyze image features
            metadata = self._extract_metadata(image)

            # Simple educational content heuristic detection
            structure = self._analyze_educational_content(text)

            # Create and return result
            optional_data = {
                'tables': tables,
                'images': [self._get_image_info(image)],
            }

            return ParsingResult(
                text=text,
                metadata=metadata,
                pages=1,  # Images typically have 1 page
                structure=structure,
                optional_data=optional_data,
            )

        except Exception as e:
            self.logger.error(f'Image parsing failed: {e}')
            return ParsingResult(text='', error=f'Image parsing failed: {e!s}')

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR quality.

        Args:
            image: PIL Image object

        Returns:
            Processed image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')

        # Additional preprocessing steps can be added, such as:
        # - Contrast adjustment
        # - Noise reduction
        # - Binarization
        # - Rotation correction
        # But these might need to be adjusted based on specific requirements

        return image

    def _extract_tables(self, image: Image.Image) -> list[dict[str, Any]]:
        """
        Attempt to extract tables from an image.

        Args:
            image: PIL Image object

        Returns:
            List of table data
        """
        # Currently returns an empty list; actual implementation would need specialized
        # table detection and extraction libraries
        # Consider using OpenCV or specialized table OCR tools
        return []

    def _extract_metadata(self, image: Image.Image) -> dict[str, Any]:
        """
        Extract metadata from an image.

        Args:
            image: PIL Image object

        Returns:
            Image metadata
        """
        return {
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'mode': image.mode,
            'dpi': image.info.get('dpi'),
        }

    def _analyze_educational_content(self, text: str) -> dict[str, Any]:
        """
        Simple heuristic identification of educational content.

        Args:
            text: Text content extracted by OCR

        Returns:
            Structured educational content information
        """
        # Currently returns an empty dictionary; actual implementation would need
        # specific educational content identification logic
        return {}

    def _get_image_info(self, image: Image.Image) -> dict[str, Any]:
        """
        Get basic information about an image.

        Args:
            image: PIL Image object

        Returns:
            Dictionary of image information
        """
        return {
            'width': image.width,
            'height': image.height,
            'format': image.format,
        }


# Register the parser
ParserRegistry.register(ImageParser)
