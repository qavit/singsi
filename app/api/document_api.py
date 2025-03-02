import json
from typing import Any

from fastapi import APIRouter, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from app.models.document import Document, DocumentMetadata
from app.services.document.document_manager import document_manager

router = APIRouter(prefix='/documents', tags=['documents'])

CHUNK_SIZE = 1024 * 1024  # 1MB chunks


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
        doc = await document_manager.process_document(
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


@router.get('/{document_id}')
async def get_document(document_id: str) -> Document:
    """Get document metadata by ID."""
    doc = await document_manager.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Document not found',
        )
    return doc


@router.get('/{document_id}/download')
async def download_document(document_id: str) -> StreamingResponse:
    """Download document content."""
    doc = await document_manager.get_document(document_id)
    if not doc or not doc.storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Document not found',
        )

    try:
        file_handle, content_type = await document_manager.storage.get_file(
            doc.storage_path
        )

        async def file_streamer():
            """Stream file in chunks."""
            while True:
                chunk = file_handle.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk
            file_handle.close()

        return StreamingResponse(
            content=file_streamer(),
            media_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{doc.filename}"',
                'Content-Length': str(doc.file_size),
            },
        )
    except Exception as e:
        if 'file_handle' in locals():
            file_handle.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error downloading file: {e!s}',
        ) from e


@router.delete('/{document_id}')
async def delete_document(document_id: str) -> dict[str, str]:
    """Delete document."""
    success = await document_manager.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Document not found',
        )
    return {'status': 'Document deleted successfully'}


@router.get('/')
async def list_documents(
    page: int = 1,
    per_page: int = 10,
    type: str | None = None,
) -> dict[str, Any]:  # Fix: change 'any' to 'Any'
    """List all documents with pagination."""
    documents, total = await document_manager.list_documents(
        page=page,
        per_page=per_page,
        doc_type=type,
    )
    return {
        'items': documents,
        'total': total,
        'page': page,
        'per_page': per_page,
    }
