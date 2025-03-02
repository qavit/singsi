"""Tests for the AI API endpoints."""

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.ai_api import router as ai_router

app = FastAPI()
app.include_router(ai_router, prefix='/api/v1')
client = TestClient(app)


@pytest.mark.api
def test_process_text():
    """
    Test the process-text endpoint using integration testing approach.

    Note: This is a test that communicates with the real API, so it requires
    valid environment variables. If mocked responses are needed, consider
    mocking the OpenAI client rather than FastAPI dependencies.
    """
    # Use a simple text request
    response = client.post(
        '/api/v1/ai/process-text',
        json={
            'text': 'Just reply with the exact text: "This is a test response"',
            'options': {'temperature': 0},
        },
    )

    # Basic validation
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'text' in data
    assert 'model' in data
    assert isinstance(data['text'], str)  # Only check type, not exact content

    # Check if response contains the text (not exact matching)
    assert 'test response' in data['text'].lower()


@pytest.mark.api
def test_status():
    """Test the status endpoint."""
    response = client.get('/api/v1/ai/status')

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['status'] == 'ready'
    assert 'model' in data  # Check existence, not specific value
    assert isinstance(data['model'], str)
