"""Tests for the OpenAIService implementation."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai.implementations.openai_service import (
    DocumentAnalysisRequest,
    OpenAIService,
)


class TestOpenAIService:
    """Test suite for OpenAIService."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        with patch(
            'app.services.ai.implementations.openai_service.AsyncOpenAI'
        ) as mock_client:
            instance = mock_client.return_value
            # Setup default behaviors
            instance.models = AsyncMock()
            instance.models.list = AsyncMock()
            instance.chat = MagicMock()
            instance.chat.completions = MagicMock()
            instance.chat.completions.create = AsyncMock()

            yield instance

    @pytest.mark.asyncio
    async def test_initialize(self, mock_openai_client):
        """Test initializing the OpenAI service."""
        # Arrange
        service = OpenAIService(api_key='test_key')

        # Act
        result = await service.initialize()

        # Assert
        assert result is True
        assert service.initialized is True
        mock_openai_client.models.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_failure(self, mock_openai_client):
        """Test initialize failure handling."""
        # Arrange
        service = OpenAIService(api_key='test_key')
        mock_openai_client.models.list.side_effect = Exception('API error')

        # Act
        result = await service.initialize()

        # Assert
        assert result is False
        assert service.initialized is False

    @pytest.mark.asyncio
    async def test_process_text(self, mock_openai_client):
        """Test processing text."""
        # Arrange
        service = OpenAIService(api_key='test_key', model='test-model')
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'This is a test response'
        mock_response.model = 'test-model'
        mock_response.usage = MagicMock()
        mock_response.usage.model_dump.return_value = {'total_tokens': 10}

        mock_openai_client.chat.completions.create.return_value = mock_response

        # Act
        result = await service.process_text('Hello, world!')

        # Assert
        assert result['text'] == 'This is a test response'
        assert result['model'] == 'test-model'
        assert result['usage'] == {'total_tokens': 10}
        mock_openai_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_document_with_content(self, mock_openai_client):
        """Test analyzing a document with binary content."""
        # Arrange
        service = OpenAIService(api_key='test_key')
        mock_response = {'text': 'Document analysis', 'model': 'test-model'}

        with patch.object(
            service, 'process_text', new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            # Act
            request = DocumentAnalysisRequest(
                content=b'test content',
                filename='test.pdf',
                content_type='application/pdf',
            )
            result = await service.analyze_document(request)

            # Assert
            assert result == mock_response
            # Verify process_text was called with the right prompt
            mock_process.assert_called_once()
            call_args = mock_process.call_args[0][0]
            assert 'Analyze this document:' in call_args
            assert 'test.pdf' in call_args
            assert 'application/pdf' in call_args

    @pytest.mark.asyncio
    async def test_analyze_document_with_text(self, mock_openai_client):
        """Test analyzing a document with text content."""
        # Arrange
        service = OpenAIService(api_key='test_key')
        mock_response = {'text': 'Document analysis', 'model': 'test-model'}

        with patch.object(
            service, 'process_text', new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            # Act
            result = await service.analyze_document(
                request=DocumentAnalysisRequest(document='test document')
            )

            # Assert
            assert result == mock_response
            mock_process.assert_called_once()
            assert 'Analyze document: test document' in mock_process.call_args[0][0]

    @pytest.mark.asyncio
    async def test_analyze_document_with_kwargs(self, mock_openai_client):
        """Test analyzing a document with kwargs instead of request object."""
        # Arrange
        service = OpenAIService(api_key='test_key')
        mock_response = {'text': 'Document analysis', 'model': 'test-model'}

        with patch.object(
            service, 'process_text', new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            # Act
            result = await service.analyze_document(document='test document')

            # Assert
            assert result == mock_response
            mock_process.assert_called_once()
            assert 'Analyze document: test document' in mock_process.call_args[0][0]

    @pytest.mark.asyncio
    async def test_analyze_document_missing_inputs(self, mock_openai_client):
        """Test error handling when neither content nor document is provided."""
        # Arrange
        service = OpenAIService(api_key='test_key')

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.analyze_document(request=DocumentAnalysisRequest())

        assert 'Either content or document must be provided' in str(exc_info.value)
