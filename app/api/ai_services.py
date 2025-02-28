from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
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
    """
    Process text input and return AI-generated response.

    Parameters:
        request (TextProcessingRequest): Contains the input text and optional
          processing parameters
            - text: The input text to be processed
            - options: Optional configuration parameters for text processing

    Returns:
        dict: Processed result from the AI model

    Raises:
        HTTPException: If text processing fails or AI service is unavailable
    """
    try:
        result = await ai_service.process_text(request.text, request.options)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f'AI processing failed: {e!s}'
        ) from e


@router.post('/generate-image')
async def generate_image(request: ImageGenerationRequest) -> dict[str, Any]:
    """
    Generate an image based on text prompt.

    Parameters:
        request (ImageGenerationRequest): Contains the generation parameters
            - prompt: Text description for image generation
            - options: Optional configuration parameters for image generation

    Returns:
        dict: Generated image data or reference

    Raises:
        HTTPException: If image generation fails or service is unavailable
    """
    try:
        result = await ai_service.generate_image(request.prompt, request.options)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f'Image generation failed: {e!s}'
        ) from e


@router.post('/process-image')
async def process_image(
    file: UploadFile,  # 移除預設值
    options: str = '',  # 簡化預設值
) -> dict[str, Any]:
    """
    Process uploaded image file with AI analysis.

    Parameters:
        file (UploadFile): The uploaded image file
        options (str): JSON string containing processing options, defaults to
          "{}"

    Returns:
        dict: Processing results containing:
            - filename: Name of the processed file
            - content_type: MIME type of the file
            - size: File size in bytes
            - status: Processing status

    Raises:
        HTTPException: If file is not an image or processing fails
    """
    if not file:
        file = File(...)
    if not options:
        options = '{}'

    try:
        # Read uploaded file content
        content = await file.read()

        # Validate file type
        content_type = file.content_type or ''
        if not content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail='Only image files are allowed')

        return {
            'filename': file.filename,
            'content_type': file.content_type,
            'size': len(content),
            'status': 'processed',
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f'Image processing failed: {e!s}'
        ) from e


@router.get('/status')
async def check_ai_status() -> dict[str, Any]:
    """
    Check the current status of AI service and model.

    Returns:
        dict: Service status information containing:
            - status: Current state ("ready" or "not_initialized")
            - model: Model information if initialized

    Note:
        This endpoint is useful for health checks and service monitoring
    """
    if not ai_service.initialized:
        return {'status': 'not_initialized'}
    return {'status': 'ready', 'model': ai_service.model['name']}
