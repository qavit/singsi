"""OpenAIService implementation based on the AIService interface."""

import logging
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from app.services.ai.base.ai_service_abstract import AIService
from app.utils.prompts import prompt_library


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
        self,
        text: str,
        options: dict[str, Any] | None = None,
        template_name: str | None = None,
        template_vars: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process and generate a text completion based on the given text or template.

        Args:
            text: The input text (used if no template is provided)
            options: Additional options for the API call
            template_name: Name of the prompt template to use
            template_vars: Variables to substitute in the template

        Returns:
            dict with response text, model info, and usage statistics
        """
        if options is None:
            options = {}

        messages = None

        # Use template if provided
        if template_name and template_vars:
            try:
                template = prompt_library.get_template(template_name)
                messages = template.format(**template_vars)
            except (KeyError, ValueError) as e:
                logging.warning(
                    f'Template error: {e}, falling back to direct text input'
                )

        # Fall back to direct text input if template is not used or fails
        if not messages:
            messages = [
                {'role': 'system', 'content': 'You are a helpful teaching assistant.'},
                {'role': 'user', 'content': text},
            ]

        # Process with OpenAI API
        response = await self.client.chat.completions.create(
            model=options.get('model', self.model),
            messages=messages,
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
                # Use the document_analysis template
                return await self.process_text(
                    text='',  # Not used when template is provided
                    options=request.options,
                    template_name='document_analysis',
                    template_vars={
                        'document_type': request.content_type or 'unknown',
                        'content': (
                            f'[Binary {request.filename or "unnamed"} file,'
                            f'size: {len(request.content)} bytes]'
                        ),
                    },
                )
            # Handle text document
            elif request.document is not None:
                # Use the document_analysis template
                return await self.process_text(
                    text='',  # Not used when template is provided
                    options=request.options,
                    template_name='document_analysis',
                    template_vars={
                        'document_type': 'text',
                        'content': request.document,
                    },
                )
            else:
                raise ValueError('Either content or document must be provided')
        except Exception as e:
            logging.error(f'Error in document analysis: {e}')
            raise

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response based on the provided prompt."""
        try:
            # Allow specifying template or fallback to direct prompt
            template_name = kwargs.get('template_name')
            template_vars = kwargs.get('template_vars')

            result = await self.process_text(
                text=prompt, template_name=template_name, template_vars=template_vars
            )
            return result['text']
        except Exception as e:
            logging.error(f'Error in generating response: {e}')
            raise

    async def analyze_image(
        self,
        image_path_or_content,
        description: str = '',
    ) -> dict[str, Any]:
        """
        Analyze an image. Support both file path and binary content.
        """
        # TODO: Implement image analysis functionality using Vision API
        try:
            # Use image_analysis template if we have a description
            if description:
                analysis_result = await self.process_text(
                    text='',
                    template_name='image_analysis',
                    template_vars={'image_description': description},
                )

                return {
                    'size': len(image_path_or_content)
                    if isinstance(image_path_or_content, bytes | bytearray)
                    else 0,
                    'analysis': analysis_result['text'],
                }

            # Fallback for now
            if isinstance(image_path_or_content, bytes | bytearray):
                return {
                    'size': len(image_path_or_content),
                    'analysis': 'Binary image analysis is not fully implemented yet.',
                }
            else:
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
