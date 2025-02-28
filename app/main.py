from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai_services import router as ai_router
from app.api.document import router as document_router
from app.core.config import settings

app = FastAPI(
    title='SingSi.AI',
    description='AI-powered teaching assistant API',
    version='0.1.0',
)

# Set CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

# Add routers
app.include_router(ai_router, prefix='/api/v1')
app.include_router(document_router, prefix=settings.API_V1_STR)


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'Welcome to SingSi.AI Backend'}


@app.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'healthy'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
