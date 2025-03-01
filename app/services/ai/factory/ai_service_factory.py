"""Factory module to create AI service instances using dependency injection from
configuration.
"""

from app.core.config import settings
from app.services.ai.base.ai_service_abstract import AIService
from app.services.ai.implementations.openai_service import OpenAIService

# Future implementations can be imported here:
# from app.services.ai.implementations.gemini_service import GeminiService
# from app.services.ai.implementations.claude_service import ClaudeService
# from app.services.ai.implementations.deepseek_service import DeepSeekService


def create_ai_service(
    provider: str | None = None, api_key: str | None = None, model: str | None = None
) -> AIService:
    """
    Create an instance of AIService based on the given provider.
    Uses dependency injection.
    """
    provider = provider or settings.DEFAULT_AI_PROVIDER
    if provider.lower() == 'openai':
        return OpenAIService(
            api_key=api_key or settings.OPENAI_API_KEY.get_secret_value(),
            model=model or settings.OPENAI_DEFAULT_MODEL,
        )
    elif provider.lower() == 'gemini':
        raise NotImplementedError('GeminiService is not implemented yet.')
    elif provider.lower() == 'claude':
        raise NotImplementedError('ClaudeService is not implemented yet.')
    elif provider.lower() == 'deepseek':
        raise NotImplementedError('DeepSeekService is not implemented yet.')
    else:
        raise ValueError(f'Unknown provider: {provider}')
