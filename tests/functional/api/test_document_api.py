import json

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.document import router as document_router

app = FastAPI()
app.include_router(document_router)
client = TestClient(app)


@pytest.fixture
def test_file_content():
    """Create test file content."""
    return b'Test file content'


@pytest.fixture
def test_metadata():
    """Create test metadata."""
    return {
        'title': 'Test Document',
        'description': 'Test Description',
        'subject': 'Testing',
        'grade_level': '5',
        'tags': ['test', 'document'],
    }


@pytest.mark.functional
def test_upload_document(test_file_content, test_metadata):
    """Test document upload endpoint."""
    files = {'file': ('test.txt', test_file_content, 'text/plain')}
    data = {'metadata': json.dumps(test_metadata)}

    response = client.post('/documents/', files=files, data=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result['filename'] == 'test.txt'
    assert result['content_type'] == 'text/plain'
    assert result['metadata']['title'] == test_metadata['title']
    assert 'analysis_results' in result


@pytest.mark.functional
def test_upload_invalid_document():
    """Test uploading invalid document type."""
    files = {'file': ('test.xyz', b'Invalid content', 'application/unknown')}
    data = {'metadata': '{}'}

    response = client.post('/documents/', files=files, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Unsupported file type' in response.json()['detail']


@pytest.mark.functional
def test_upload_document_without_metadata(test_file_content):
    """Test document upload without metadata."""
    files = {'file': ('test.txt', test_file_content, 'text/plain')}

    response = client.post('/documents/', files=files)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result['filename'] == 'test.txt'
    assert result['metadata']['title'] == 'test.txt'
