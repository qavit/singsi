"""OpenAIService implementation based on the AIService interface."""

import logging
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from app.services.ai.base.ai_service_abstract import AIService


@dataclass
class DocumentAnalysisRequest:
    """Container for document analysis parameters."""

    content: bytes | None = None
    filename: str | None = None
    content_type: str | None = None
    document: str | None = None
    options: dict[str, Any] | None = None


class OpenAIService(AIService):
    """Integrated OpenAIService implementation using the asynchronous OpenAI client."""

    def __init__(self, api_key: str, model: str = 'gpt-4o-mini'):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.initialized = False

    async def initialize(self) -> bool:
        """
        Initialize the OpenAI client by validating connectivity.
        """
        try:
            await self.client.models.list()
            self.initialized = True
            return True
        except Exception as e:
            logging.error(f'Failed to initialize OpenAI client: {e}')
            return False

    async def process_text(
        self, text: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Process and generate a text completion based on the given text.
        """
        if options is None:
            options = {}
        response = await self.client.chat.completions.create(
            model=options.get('model', self.model),
            messages=[
                {'role': 'system', 'content': 'You are a helpful teaching assistant.'},
                {'role': 'user', 'content': text},
            ],
            temperature=options.get('temperature', 0.7),
        )
        return {
            'text': response.choices[0].message.content,
            'model': response.model,
            'usage': response.usage.model_dump() if response.usage else None,
        }

    async def analyze_document(
        self, request: DocumentAnalysisRequest | None = None, **kwargs
    ) -> dict[str, Any]:
        """
        Analyze document content using the OpenAI client.
        Supports both binary content and text document.
        """
        # Support both object-based and direct parameter calls
        if request is None:
            request = DocumentAnalysisRequest(**kwargs)

        try:
            # Handle binary content
            if request.content is not None:
                # Extract text or process binary content according to content_type
                doc_info = (
                    f'Document: {request.filename} ({request.content_type}, '
                    f'{len(request.content)} bytes)'
                )
                return await self.process_text(
                    f'Analyze this document: {doc_info}', request.options
                )
            # Handle text document
            elif request.document is not None:
                return await self.process_text(
                    f'Analyze document: {request.document}', request.options
                )
            else:
                raise ValueError('Either content or document must be provided')
        except Exception as e:
            logging.error(f'Error in document analysis: {e}')
            raise

    async def generate_response(self, prompt: str) -> str:
        """Generate a response based on the provided prompt."""
        try:
            result = await self.process_text(prompt)
            return result['text']
        except Exception as e:
            logging.error(f'Error in generating response: {e}')
            raise

    async def analyze_image(self, image_path_or_content) -> dict[str, Any]:
        """
        Analyze an image. Support both file path and binary content.
        """
        # TODO: Implement image analysis functionality
        try:
            # Check if input is binary content or file path
            if isinstance(image_path_or_content, bytes | bytearray):
                # Process binary content
                return {
                    'size': len(image_path_or_content),
                    'analysis': 'Binary image analysis is not fully implemented yet.',
                }
            else:
                # Process file path
                return {
                    'image_path': image_path_or_content,
                    'analysis': 'Image path analysis is not fully implemented yet.',
                }
        except Exception as e:
            logging.error(f'Error in image analysis: {e}')
            raise

    async def generate_image(self, prompt: str) -> Any:
        """Generate an image based on the provided prompt."""
        # TODO: Implement image generation functionality
        try:
            return {
                'prompt': prompt,
                'image': 'Image generation functionality is not implemented yet.',
            }
        except Exception as e:
            logging.error(f'Error in generating image: {e}')
            raise
