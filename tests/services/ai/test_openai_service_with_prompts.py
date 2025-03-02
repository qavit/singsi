"""Tests for the OpenAIService with prompt templating system."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai.implementations.openai_service import (
    DocumentAnalysisRequest,
    OpenAIService,
)
from app.utils.prompts import PromptMessage, PromptRole, PromptTemplate, prompt_library

EXPECTED_MESSAGE_COUNT = 2


class TestOpenAIServiceWithPrompts:
    """Test suite for OpenAIService integration with prompt templates."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        with patch(
            'app.services.ai.implementations.openai_service.AsyncOpenAI'
        ) as mock_client:
            instance = mock_client.return_value
            instance.models = AsyncMock()
            instance.models.list = AsyncMock()
            instance.chat = MagicMock()
            instance.chat.completions = MagicMock()
            instance.chat.completions.create = AsyncMock()

            # Setup default response behavior
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = 'This is a test response'
            mock_response.model = 'test-model'
            mock_response.usage = MagicMock()
            mock_response.usage.model_dump.return_value = {'total_tokens': 10}
            instance.chat.completions.create.return_value = mock_response

            yield instance

    @pytest.fixture
    def test_template(self):
        """Create a test prompt template."""
        return PromptTemplate(
            name='test_template',
            description='Test template for unit testing',
            version='1.0',
            template_messages=[
                PromptMessage(
                    role=PromptRole.SYSTEM,
                    content='You are a {role} specialized in {subject}.',
                ),
                PromptMessage(
                    role=PromptRole.USER,
                    content='Please {action} the following: {content}',
                ),
            ],
        )

    @pytest.mark.asyncio
    async def test_process_text_with_template(self, mock_openai_client, test_template):
        """Test processing text with a prompt template."""
        # Add test template to library
        prompt_library.add_template(test_template)

        # Create service
        service = OpenAIService(api_key='test_key')

        # Process text with template
        result = await service.process_text(
            text='This text is ignored when template is used',
            template_name='test_template',
            template_vars={
                'role': 'teacher',
                'subject': 'mathematics',
                'action': 'analyze',
                'content': 'x^2 + 5x + 6 = 0',
            },
        )

        # Verify result
        assert result['text'] == 'This is a test response'
        assert result['model'] == 'test-model'

        # Verify template was used correctly
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args[1]
        messages = call_args['messages']

        # Check correct messages were created

        assert len(messages) == EXPECTED_MESSAGE_COUNT
        assert messages[0]['role'] == 'system'
        assert 'teacher' in messages[0]['content']
        assert 'mathematics' in messages[0]['content']
        assert messages[1]['role'] == 'user'
        assert 'analyze' in messages[1]['content']
        assert 'x^2 + 5x + 6 = 0' in messages[1]['content']

    @pytest.mark.asyncio
    async def test_process_text_template_error_fallback(self, mock_openai_client):
        """Test falling back to direct text if template has an error."""
        # Create service
        service = OpenAIService(api_key='test_key')

        # Process with non-existent template
        result = await service.process_text(
            text='Direct text input',
            template_name='non_existent_template',
            template_vars={'some': 'variable'},
        )

        # Verify fallback behavior
        assert result['text'] == 'This is a test response'

        # Check that fallback messages were used
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args[1]
        messages = call_args['messages']

        assert len(messages) == EXPECTED_MESSAGE_COUNT
        assert 'Direct text input' in messages[1]['content']

    @pytest.mark.asyncio
    async def test_analyze_document_with_template(self, mock_openai_client):
        """Test document analysis using templates."""
        # Create service
        service = OpenAIService(api_key='test_key')

        # Mock process_text to verify it's called with correct template
        with patch.object(
            service, 'process_text', new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = {
                'text': 'Document analysis result',
                'model': 'test-model',
            }

            # Analyze document
            request = DocumentAnalysisRequest(
                document='Document content for testing',
            )
            await service.analyze_document(request)

            # Verify template was used
            mock_process.assert_called_once()
            call_args = mock_process.call_args

            assert call_args[1]['template_name'] == 'document_analysis'
            assert call_args[1]['template_vars']['document_type'] == 'text'
            assert (
                'Document content for testing'
                in call_args[1]['template_vars']['content']
            )

    @pytest.mark.asyncio
    async def test_analyze_image_with_description(self, mock_openai_client):
        """Test image analysis with description using templates."""
        # Create service
        service = OpenAIService(api_key='test_key')

        # Mock process_text to verify template usage
        with patch.object(
            service, 'process_text', new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = {
                'text': 'Image analysis result',
                'model': 'test-model',
            }

            # Analyze image with description
            image_data = b'mock image data'
            description = 'An image showing a classroom with students'
            result = await service.analyze_image(image_data, description=description)

            # Verify template was used
            mock_process.assert_called_once()
            call_args = mock_process.call_args

            assert call_args[1]['template_name'] == 'image_analysis'
            assert call_args[1]['template_vars']['image_description'] == description
            assert 'Image analysis result' in result['analysis']

    @pytest.mark.asyncio
    async def test_generate_response_with_template(self, mock_openai_client):
        """Test generate_response with template support."""
        # Create service
        service = OpenAIService(api_key='test_key')

        # Test with template
        with patch.object(
            service, 'process_text', new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = {
                'text': 'Generated from template',
                'model': 'test-model',
            }

            result = await service.generate_response(
                prompt='This should be ignored',
                template_name='question_generation',
                template_vars={
                    'question_count': 3,
                    'question_type': 'multiple-choice',
                    'topic': 'calculus',
                    'difficulty_level': 'college',
                    'content': 'Differential equations',
                },
            )

            # Verify correct template was used
            mock_process.assert_called_once()
            call_args = mock_process.call_args
            assert call_args[1]['template_name'] == 'question_generation'
            assert call_args[1]['template_vars']['topic'] == 'calculus'
            assert result == 'Generated from template'
