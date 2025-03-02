"""Document analysis API endpoints."""

import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.ai.base.ai_service_abstract import AIService
from app.services.ai.factory.ai_service_factory import create_ai_service
from app.services.document.integration.ai_document_analyzer import AIDocumentAnalyzer
from app.services.document.parsing_service import document_parsing_service

router = APIRouter()
logger = logging.getLogger(__name__)


class DocumentAnalysisResponse(BaseModel):
    """Document analysis response model."""

    success: bool = Field(..., description='Whether the analysis was successful')
    document_type: str = Field(
        ..., description='Type of the document (e.g., syllabus, exam)'
    )
    page_count: int = Field(..., description='Number of pages in the document')
    word_count: int | None = Field(None, description='Approximate word count')
    analysis: dict = Field(..., description='Analysis results')
    error: str | None = Field(None, description='Error message if any')


@router.post(
    '/analyze',
    response_model=DocumentAnalysisResponse,
    summary='Analyze educational document',
    description='Upload and analyze an educational document with AI',
)
async def analyze_document(
    file: UploadFile,
    ai_service: AIService,
    analysis_depth: str = Form('standard'),
):
    """
    Analyze an uploaded educational document.

    - **file**: The document file to analyze
    - **analysis_depth**: Level of analysis detail ("basic", "standard", or "deep")
    """
    ai_service = Depends(create_ai_service)
    file = await File(...).resolve()

    # Validate analysis_depth parameter
    if analysis_depth not in ['basic', 'standard', 'deep']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis depth must be 'basic', 'standard', or 'deep'",
        )

    try:
        # Read file content
        content = await file.read()

        # Check file size limit
        max_size_mb = settings.MAX_DOCUMENT_SIZE_MB
        if len(content) > max_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f'File size exceeds the maximum limit of {max_size_mb}MB',
            )

        # Get mimetype from file
        mimetype = file.content_type
        filename = file.filename

        # Parse document
        logger.info(f'Parsing document: {filename} ({mimetype})')
        parsing_result_dict = await document_parsing_service.parse_document(
            content=content, mimetype=mimetype, filename=filename
        )

        # Check if parsing was successful
        if parsing_result_dict.get('error'):
            error_msg = parsing_result_dict['error']
            logger.warning(f'Document parsing error: {error_msg}')

            # Return partial result with error
            return DocumentAnalysisResponse(
                success=False,
                document_type='unknown',
                page_count=parsing_result_dict.get('pages', 1),
                word_count=len(parsing_result_dict.get('text', '').split()),
                analysis={'parsing_result': parsing_result_dict},
                error=error_msg,
            )

        # Convert parsing result dict back to ParsingResult object for AI analysis
        from app.services.document.parser_base import ParsingResult

        parsing_result = ParsingResult(
            text=parsing_result_dict.get('text', ''),
            metadata=parsing_result_dict.get('metadata', {}),
            pages=parsing_result_dict.get('pages', 1),
            structure=parsing_result_dict.get('structure', {}),
            optional_data={
                k: v
                for k, v in parsing_result_dict.items()
                if k
                not in ['text', 'metadata', 'pages', 'structure', 'success', 'error']
            },
        )

        # Initialize AI document analyzer
        ai_analyzer = AIDocumentAnalyzer(ai_service)

        # Perform AI analysis
        logger.info(f'Performing AI analysis with depth: {analysis_depth}')
        analysis_result = await ai_analyzer.analyze_document(
            parsing_result=parsing_result, analysis_depth=analysis_depth
        )

        # Check if AI analysis was successful
        if analysis_result.get('error'):
            error_msg = analysis_result['error']
            logger.warning(f'AI analysis error: {error_msg}')

            # Return partial result with error
            return DocumentAnalysisResponse(
                success=False,
                document_type=analysis_result.get('document_type', 'unknown'),
                page_count=parsing_result.pages,
                word_count=len(parsing_result.text.split()),
                analysis={
                    'parsing_result': parsing_result_dict,
                    'partial_analysis': analysis_result,
                },
                error=error_msg,
            )

        # Return successful response
        return DocumentAnalysisResponse(
            success=True,
            document_type=analysis_result.get('document_type', 'unknown'),
            page_count=parsing_result.pages,
            word_count=len(parsing_result.text.split()),
            analysis=analysis_result,
            error=None,
        )

    except Exception as e:
        logger.error(f'Document analysis failed: {e!s}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Document analysis failed: {e!s}',
        ) from e


@router.get(
    '/supported-formats',
    response_model=list[str],
    summary='Get supported document formats',
    description='Returns a list of supported document MIME types',
)
async def get_supported_formats():
    """Get list of supported document formats (MIME types)."""
    return document_parsing_service.get_supported_mimetypes()
