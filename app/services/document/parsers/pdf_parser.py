"""PDF document parser implementation."""

import io
from typing import Any

import fitz  # PyMuPDF
from pdfminer.high_level import extract_text

from app.services.document.parser_base import (
    DocumentParser,
    ParserRegistry,
    ParsingResult,
)

EXPECTED_MIN_TEXT_LENGTH = 100


class PDFParser(DocumentParser):
    """PDF parser using both PyMuPDF and PDFMiner for robust text extraction."""

    @classmethod
    def supported_mimetypes(cls) -> list[str]:
        """Return list of supported MIME types."""
        return ['application/pdf']

    async def parse(self, content: bytes, filename: str | None = None) -> ParsingResult:
        """
        Parse PDF document.

        This implementation uses both PyMuPDF for structure extraction
        and PDFMiner as a fallback for better text extraction in some cases.
        """
        try:
            # Use PyMuPDF (fitz) for main extraction
            text, metadata, structure = self._parse_with_pymupdf(content)

            # If text extraction failed or resulted in very little text,
            # try PDFMiner as a fallback
            if not text or len(text.strip()) < EXPECTED_MIN_TEXT_LENGTH:
                fallback_text = self._parse_with_pdfminer(content)
                if len(fallback_text.strip()) > len(text.strip()):
                    text = fallback_text

            # If we successfully extracted text with either method, don't report an
            # error
            if text and len(text.strip()) >= EXPECTED_MIN_TEXT_LENGTH:
                return ParsingResult(
                    text=text,
                    metadata=metadata,
                    pages=structure.get('page_count', 1),
                    structure=structure,
                )
            else:
                # Text extraction was poor, report as warning but return what we have
                return ParsingResult(
                    text=text,
                    metadata=metadata,
                    pages=structure.get('page_count', 1),
                    structure=structure,
                    error=(
                        'Extracted text is minimal or empty; document may be scanned '
                        'or image-based.'
                    ),
                )
        except Exception as e:
            # Fallback to simple extraction if advanced parsing fails
            try:
                simple_text = self._parse_with_pdfminer(content)
                if simple_text and len(simple_text.strip()) > 0:
                    # If fallback succeeded, return result with warning
                    return ParsingResult(
                        text=simple_text,
                        metadata={'extraction_method': 'pdfminer_fallback'},
                        pages=1,  # We don't know how many pages without PyMuPDF
                        error=f'Using fallback extraction due to error: {e!s}',
                    )
                else:
                    return ParsingResult(
                        text='',
                        error=f'PDF parsing failed, no text could be extracted: {e!s}',
                    )
            except Exception as fallback_e:
                return ParsingResult(
                    text='', error=f'PDF parsing failed: {fallback_e!s}'
                )

    def _parse_with_pymupdf(
        self, content: bytes
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Extract text and structure using PyMuPDF."""
        doc = fitz.open(stream=content, filetype='pdf')

        # Extract metadata
        metadata = {
            'title': doc.metadata.get('title', ''),
            'author': doc.metadata.get('author', ''),
            'subject': doc.metadata.get('subject', ''),
            'keywords': doc.metadata.get('keywords', ''),
            'creator': doc.metadata.get('creator', ''),
            'producer': doc.metadata.get('producer', ''),
            'creation_date': doc.metadata.get('creationDate', ''),
            'modification_date': doc.metadata.get('modDate', ''),
        }

        # Extract structure - handle possible errors with TOC
        structure = {'page_count': len(doc), 'form_fields': []}

        # Safely get TOC (table of contents)
        try:
            toc = doc.get_toc()
            if isinstance(toc, list):
                structure['toc'] = toc
            else:
                structure['toc'] = []
        except Exception:
            structure['toc'] = []  # Empty list if TOC extraction fails

        # Add form fields if any
        try:
            for page in doc:
                if page.widgets:
                    for widget in page.widgets:
                        structure['form_fields'].append(
                            {
                                'field_name': widget.field_name,
                                'field_type': widget.field_type,
                                'field_value': widget.field_value,
                            }
                        )
        except Exception:
            # If form fields extraction fails, just provide an empty list
            structure['form_fields'] = []

        # Extract text with layout analysis
        full_text = ''
        for page in doc:
            try:
                text = page.get_text()
                full_text += text + '\n\n'
            except Exception:
                # If text extraction fails for a page, continue with other pages
                continue

        doc.close()
        return full_text, metadata, structure

    def _parse_with_pdfminer(self, content: bytes) -> str:
        """Extract text using PDFMiner as a fallback."""
        pdf_file = io.BytesIO(content)
        return extract_text(pdf_file)


# Register the parser
ParserRegistry.register(PDFParser)
