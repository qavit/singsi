import io

import pytest

from app.models.document import Document, DocumentType
from app.services.document_service import document_service


@pytest.fixture
def sample_text_file():
    """Create a sample text file for testing."""
    content = b'Hello, this is a test document.'
    return io.BytesIO(content)


@pytest.fixture
def sample_pdf_file():
    """Create a mock PDF file for testing."""
    content = b'%PDF-1.4\n...'  # Minimal PDF header
    return io.BytesIO(content)


@pytest.fixture
def sample_metadata():
    """Create sample document metadata."""
    return {
        'title': 'Test Document',
        'description': 'This is a test document',
        'subject': 'Testing',
        'grade_level': '5',
        'tags': ['test', 'document', 'sample'],
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_document_type():
    """Test document type detection."""
    # Test PDF detection
    assert (
        document_service._detect_document_type('test.pdf', 'application/pdf')
        == DocumentType.PDF
    )

    # Test Word detection
    assert (
        document_service._detect_document_type(
            'test.docx',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        == DocumentType.WORD
    )

    # Test text detection
    assert (
        document_service._detect_document_type('test.txt', 'text/plain')
        == DocumentType.TEXT
    )

    # Test markdown detection
    assert (
        document_service._detect_document_type('test.md', 'text/markdown')
        == DocumentType.MARKDOWN
    )

    # Test image detection
    assert (
        document_service._detect_document_type('test.jpg', 'image/jpeg')
        == DocumentType.IMAGE
    )

    # Test unsupported type
    with pytest.raises(ValueError):
        document_service._detect_document_type('test.xyz', 'application/unknown')


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_text_document(sample_text_file, sample_metadata):
    """Test processing a text document."""
    doc = await document_service.process_document(
        file=sample_text_file,
        filename='test.txt',
        content_type='text/plain',
        metadata=sample_metadata,
    )

    assert isinstance(doc, Document)
    assert doc.filename == 'test.txt'
    assert doc.content_type == 'text/plain'
    assert doc.type == DocumentType.TEXT
    assert doc.metadata.title == sample_metadata['title']
    assert doc.metadata.tags == sample_metadata['tags']

    assert 'text' in doc.analysis_results
    assert 'model' in doc.analysis_results
    assert 'usage' in doc.analysis_results


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_pdf_document(sample_pdf_file, sample_metadata):
    """Test processing a PDF document."""
    doc = await document_service.process_document(
        file=sample_pdf_file,
        filename='test.pdf',
        content_type='application/pdf',
        metadata=sample_metadata,
    )

    assert isinstance(doc, Document)
    assert doc.filename == 'test.pdf'
    assert doc.type == DocumentType.PDF
    assert doc.metadata.title == sample_metadata['title']

    assert 'text' in doc.analysis_results
    assert 'model' in doc.analysis_results
    assert 'usage' in doc.analysis_results


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_document_without_metadata(sample_text_file):
    """Test processing document without metadata."""
    doc = await document_service.process_document(
        file=sample_text_file, filename='test.txt', content_type='text/plain'
    )

    assert isinstance(doc, Document)
    assert doc.filename == 'test.txt'
    assert doc.metadata.title == 'test.txt'  # Should use filename as title
    assert isinstance(doc.metadata.tags, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_document_with_invalid_type():
    """Test processing document with invalid type."""
    invalid_file = io.BytesIO(b'Invalid content')

    with pytest.raises(ValueError) as exc_info:
        await document_service.process_document(
            file=invalid_file, filename='test.xyz', content_type='application/unknown'
        )

    assert 'Unsupported file type' in str(exc_info.value)
