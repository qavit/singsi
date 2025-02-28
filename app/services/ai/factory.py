from typing import Literal

from app.services.ai.base import AIProvider
from app.services.ai.providers.openai_provider import OpenAIProvider

ProviderType = Literal['openai', 'anthropic']


class AIProviderFactory:
    """Factory for creating AI service providers."""

    @staticmethod
    def create(provider: ProviderType) -> AIProvider:
        if provider == 'openai':
            return OpenAIProvider()
        # Add more providers here
        raise ValueError(f'Unknown provider: {provider}')
