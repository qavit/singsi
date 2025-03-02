"""Document parsing service."""

import logging
from typing import Any

from app.services.document.parser_base import ParserRegistry, ParsingResult


class DocumentParsingService:
    """Service for parsing different document types."""

    async def parse_document(
        self, content: bytes, mimetype: str, filename: str | None = None
    ) -> dict[str, Any]:
        """
        Parse document content based on its MIME type.

        Args:
            content: Binary content of the document
            mimetype: MIME type of the document
            filename: Optional filename for reference

        Returns:
            Dictionary containing parsing results
        """
        # Normalize mimetype to handle parameters
        mimetype = mimetype.split(';')[0].strip().lower()

        # Get appropriate parser
        parser_class = ParserRegistry.get_parser(mimetype)

        if not parser_class:
            logging.warning(f'No parser found for MIME type: {mimetype}')
            return ParsingResult(
                text='', error=f'Unsupported document type: {mimetype}'
            ).to_dict()

        # Create parser instance and parse document
        parser = parser_class()
        result = await parser.parse(content, filename)

        # Ensure to wait for parsing result before calling to_dict
        return result.to_dict()

    def get_supported_mimetypes(self) -> list[str]:
        """Get list of all supported MIME types."""
        return ParserRegistry.get_supported_types()


# Create a global instance for dependency injection
document_parsing_service = DocumentParsingService()
