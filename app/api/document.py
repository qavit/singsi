import json

from fastapi import APIRouter, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from app.models.document import Document, DocumentMetadata
from app.services.document_service import document_service

router = APIRouter(prefix='/documents', tags=['documents'])


@router.post('/')
async def upload_document(
    file: UploadFile,
    metadata: str = Form(default='{}'),  # Use Form to properly handle multipart data
) -> Document:
    """Upload and process a document."""
    try:
        # Parse metadata with better error handling
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid JSON in metadata: {e!s}',
            ) from e

        # Only use filename as fallback if title is not provided
        if 'title' not in meta_dict:
            meta_dict['title'] = file.filename

        # Create metadata model
        doc_metadata = DocumentMetadata(**meta_dict)

        # Process document
        doc = await document_service.process_document(
            file=file.file,
            filename=file.filename,
            content_type=file.content_type,
            metadata=doc_metadata.model_dump(),
        )
        return doc
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid metadata format: {e!s}',
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Document processing failed: {e!s}',
        ) from e
