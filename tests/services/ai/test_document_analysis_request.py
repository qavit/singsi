"""Tests for the DocumentAnalysisRequest data class."""

from app.services.ai.implementations.openai_service import DocumentAnalysisRequest


def test_document_analysis_request_creation():
    """Test creating a DocumentAnalysisRequest with various parameters."""
    # Test with content
    request1 = DocumentAnalysisRequest(
        content=b'test content', filename='test.pdf', content_type='application/pdf'
    )
    assert request1.content == b'test content'
    assert request1.filename == 'test.pdf'
    assert request1.content_type == 'application/pdf'
    assert request1.document is None
    assert request1.options is None

    # Test with document
    request2 = DocumentAnalysisRequest(document='test document')
    assert request2.document == 'test document'
    assert request2.content is None

    # Test with options
    options = {'temperature': 0.5}
    request3 = DocumentAnalysisRequest(document='test', options=options)
    assert request3.options == options


def test_document_analysis_request_defaults():
    """Test the default values for DocumentAnalysisRequest."""
    request = DocumentAnalysisRequest()
    assert request.content is None
    assert request.filename is None
    assert request.content_type is None
    assert request.document is None
    assert request.options is None
