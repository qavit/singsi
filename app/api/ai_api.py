from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.config import settings
from app.services.ai.base.ai_service_abstract import AIService
from app.services.ai.factory.ai_service_factory import create_ai_service

router = APIRouter(prefix='/ai', tags=['ai'])


# Dependency to get AI service instance
async def get_ai_service() -> AIService:
    service = create_ai_service(
        provider=settings.DEFAULT_AI_PROVIDER,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
        model=settings.OPENAI_DEFAULT_MODEL,
    )
    await service.initialize()
    return service


# Create a type annotation with the dependency
AIServiceDep = Annotated[AIService, Depends(get_ai_service)]


class TextProcessingRequest(BaseModel):
    text: str
    options: dict[str, Any] | None = None


class ImageGenerationRequest(BaseModel):
    prompt: str
    options: dict[str, Any] | None = None


@router.post('/process-text')
async def process_text(
    request: TextProcessingRequest, ai_service: AIServiceDep
) -> dict[str, Any]:
    """Process text input using AI model."""
    try:
        return await ai_service.process_text(request.text, request.options)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'AI processing failed: {e!s}',
        ) from e


@router.post('/process-image')
async def process_image(
    file: UploadFile, ai_service: AIServiceDep, options: str = ''
) -> dict[str, Any]:
    """Process uploaded image file with AI analysis."""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only image files are allowed',
        )

    try:
        content = await file.read()
        # TODO: Implement image analysis functionality
        return {
            'filename': file.filename,
            'content_type': file.content_type,
            'size': len(content),
            'status': 'processed',
            'message': 'Image analysis is partially implemented.',
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Image processing failed: {e!s}',
        ) from e


@router.post('/generate-image')
async def generate_image(
    request: ImageGenerationRequest, ai_service: AIServiceDep
) -> dict[str, Any]:
    """Generate an image based on text prompt."""
    try:
        return await ai_service.generate_image(request.prompt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Image generation failed: {e!s}',
        ) from e


@router.get('/status')
async def check_ai_status(ai_service: AIServiceDep) -> dict[str, Any]:
    """Check AI service and model status."""
    is_initialized = await ai_service.initialize()
    if not is_initialized:
        return {'status': 'not_initialized'}
    return {'status': 'ready', 'model': ai_service.model}
