from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai_services import router as ai_router

app = FastAPI(
    title='SingSi.AI Backend',
    description='Backend for AI Web Application',
    version='0.1.0',
)

# Add AI service routes (after CORS setup)
app.include_router(ai_router, prefix='/api/v1')

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Should be restricted in production
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'Welcome to SingSi.AI Backend'}


@app.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'healthy'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
