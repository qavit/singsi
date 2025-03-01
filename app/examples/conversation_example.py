import asyncio

from app.services.ai.factory.ai_service_factory import create_ai_service


async def main():
    ai_service = create_ai_service(provider='openai')

    question: str = 'Hello, how are you?'
    print('User question:', question)

    response: str = await ai_service.generate_response(question)
    print('AI reply:', response)


if __name__ == '__main__':
    asyncio.run(main())
