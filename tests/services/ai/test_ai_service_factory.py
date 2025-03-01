"""Tests for the AI service factory."""

import pytest

from app.services.ai.factory import create_ai_service
from app.services.ai.implementations.openai_service import OpenAIService


def test_create_ai_service_openai():
    """Test creating an OpenAI service."""
    service = create_ai_service(
        provider='openai', api_key='test_key', model='test_model'
    )

    assert isinstance(service, OpenAIService)
    assert service.model == 'test_model'


def test_create_ai_service_unknown_provider():
    """Test error handling for unknown provider."""
    with pytest.raises(ValueError) as exc_info:
        create_ai_service(provider='unknown')

    assert 'Unknown provider: unknown' in str(exc_info.value)


def test_create_ai_service_unimplemented_providers():
    """Test error handling for providers that aren't implemented yet."""
    future_providers = ['gemini', 'claude', 'deepseek']

    for provider in future_providers:
        with pytest.raises(NotImplementedError) as exc_info:
            create_ai_service(provider=provider)

        error_message = str(exc_info.value).lower()
        assert provider.lower() in error_message
        assert 'not implemented yet' in error_message
