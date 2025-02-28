from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.services.ai_service import ai_service

router = APIRouter(prefix='/ai', tags=['ai'])


class TextProcessingRequest(BaseModel):
    text: str
    options: dict[str, Any] | None = None


class ImageGenerationRequest(BaseModel):
    prompt: str
    options: dict[str, Any] | None = None


@router.post('/process-text')
async def process_text(request: TextProcessingRequest) -> dict[str, Any]:
    """Process text input using AI model."""
    try:
        result = await ai_service.process_text(request.text, request.options)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'AI processing failed: {e!s}',
        ) from e


@router.post('/process-image')
async def process_image(file: UploadFile, options: str = '') -> dict[str, Any]:
    """Process uploaded image file with AI analysis."""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only image files are allowed',
        )

    try:
        content = await file.read()
        return {
            'filename': file.filename,
            'content_type': file.content_type,
            'size': len(content),
            'status': 'processed',
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Image processing failed: {e!s}',
        ) from e


@router.post('/generate-image')
async def generate_image(request: ImageGenerationRequest) -> dict[str, Any]:
    """Generate an image based on text prompt."""
    try:
        result = await ai_service.generate_image(request.prompt, request.options)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Image generation failed: {e!s}',
        ) from e


@router.get('/status')
async def check_ai_status() -> dict[str, Any]:
    """Check AI service and model status."""
    if not ai_service.initialized:
        return {'status': 'not_initialized'}
    return {'status': 'ready', 'model': ai_service.model['name']}
