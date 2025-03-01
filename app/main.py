from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.ai import router as ai_router
from app.api.document import router as document_router
from app.core.config import settings

# Define paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

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

# Mount static files
app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

# Setup templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Add API routers
app.include_router(ai_router, prefix='/api/v1')
app.include_router(document_router, prefix=settings.API_V1_STR)


@app.get('/', response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    """Render homepage template."""
    return templates.TemplateResponse(name='index.html', context={'request': request})


@app.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'healthy'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
