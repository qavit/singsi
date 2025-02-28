import pytest

from app.services.ai.factory import AIProviderFactory


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openai_provider() -> None:
    """Test OpenAI provider basic functionality."""
    # Create provider instance
    provider = AIProviderFactory.create('openai')

    # Initialize provider
    print('Initializing provider...')
    initialized = await provider.initialize()
    assert initialized is True

    # Test text processing
    print('\nTesting text processing...')
    result = await provider.process_text(
        '請幫我設計一個國小五年級的數學題目，主題是分數計算。',
        options={'model': 'gpt-4o-mini', 'temperature': 0.7},
    )
    assert 'text' in result
    assert 'model' in result
    assert 'usage' in result

    print('Response:', result['text'])
    print('Model:', result['model'])
    print('Usage:', result['usage'])


if __name__ == '__main__':
    pytest.main(['-v', __file__])
