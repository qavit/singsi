import json
import mimetypes
from collections.abc import Sequence
from pathlib import Path
from typing import Any, BinaryIO

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.db.session import AsyncSessionLocal
from app.models.document import Document, DocumentDB, DocumentMetadata, DocumentType
from app.services.ai.factory import AIProviderFactory
from app.services.storage.local import storage_provider


class DocumentService:
    """Service for document processing and analysis."""

    def __init__(self, session_factory: sessionmaker = AsyncSessionLocal) -> None:
        self.ai_provider = AIProviderFactory.create('openai')
        self.storage = storage_provider
        self.session_factory = session_factory

    def _detect_document_type(self, filename: str, content_type: str) -> DocumentType:
        """Detect document type from filename and content type."""
        ext = Path(filename).suffix.lower()
        if ext in {'.pdf'}:
            return DocumentType.PDF
        elif ext in {'.doc', '.docx'}:
            return DocumentType.WORD
        elif ext in {'.txt'}:
            return DocumentType.TEXT
        elif ext in {'.md', '.markdown'}:
            return DocumentType.MARKDOWN
        elif content_type.startswith('image/'):
            return DocumentType.IMAGE
        else:
            raise ValueError(f'Unsupported file type: {filename} ({content_type})')

    async def process_document(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        """Process and analyze uploaded document."""
        async with self.session_factory() as session:
            content = file.read()
            content_type = (
                content_type
                or mimetypes.guess_type(filename)[0]
                or 'application/octet-stream'
            )

            # Save file to storage
            storage_path = await self.storage.save_file(file, filename, content_type)

            # Create document model
            doc = Document(
                filename=filename,
                content_type=content_type,
                file_size=len(content),
                type=self._detect_document_type(filename, content_type),
                metadata=DocumentMetadata(**(metadata or {'title': filename})),
                storage_path=storage_path,
            )

            # Analyze document content
            doc.analysis_results = await self.ai_provider.analyze_document(
                content=content,
                filename=filename,
                content_type=content_type,
            )

            # Create DB model
            db_doc = DocumentDB(
                id=doc.id,
                filename=doc.filename,
                content_type=doc.content_type,
                file_size=doc.file_size,
                type=doc.type,
                doc_metadata=json.dumps(doc.metadata.model_dump()),
                storage_path=doc.storage_path,
                vector_ids=json.dumps(doc.vector_ids),
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                analysis_results=json.dumps(doc.analysis_results),
            )

            # Save to database
            session.add(db_doc)
            await session.commit()

            return doc

    async def get_document(self, document_id: str) -> Document | None:
        """Get document by ID."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(DocumentDB).where(DocumentDB.id == document_id)
            )
            db_doc = result.scalar_one_or_none()

            if not db_doc:
                return None

            return Document(
                id=db_doc.id,
                filename=db_doc.filename,
                content_type=db_doc.content_type,
                file_size=db_doc.file_size,
                type=db_doc.type,
                metadata=DocumentMetadata(**json.loads(db_doc.doc_metadata)),
                storage_path=db_doc.storage_path,
                vector_ids=json.loads(db_doc.vector_ids),
                created_at=db_doc.created_at,
                updated_at=db_doc.updated_at,
                analysis_results=json.loads(db_doc.analysis_results),
            )

    async def delete_document(self, document_id: str) -> bool:
        """Delete document and its stored file."""
        async with self.session_factory() as session:
            # Get document
            result = await session.execute(
                select(DocumentDB).where(DocumentDB.id == document_id)
            )
            db_doc = result.scalar_one_or_none()

            if not db_doc or not db_doc.storage_path:
                return False

            # Delete file
            if await self.storage.delete_file(db_doc.storage_path):
                # Delete from database
                await session.delete(db_doc)
                await session.commit()
                return True
            return False

    async def list_documents(
        self,
        page: int = 1,
        per_page: int = 10,
        doc_type: str | None = None,
    ) -> tuple[Sequence[Document], int]:
        """List documents with pagination."""
        async with self.session_factory() as session:
            query = select(DocumentDB)
            if doc_type:
                query = query.where(DocumentDB.type == doc_type)

            # Get total count
            count_result = await session.execute(query)
            total = len(count_result.scalars().all())

            # Get paginated results
            query = query.offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            db_docs = result.scalars().all()

            # Convert to Pydantic models
            documents = [
                Document(
                    id=doc.id,
                    filename=doc.filename,
                    content_type=doc.content_type,
                    file_size=doc.file_size,
                    type=doc.type,
                    metadata=DocumentMetadata(**json.loads(doc.doc_metadata)),
                    storage_path=doc.storage_path,
                    vector_ids=json.loads(doc.vector_ids),
                    created_at=doc.created_at,
                    updated_at=doc.updated_at,
                    analysis_results=json.loads(doc.analysis_results),
                )
                for doc in db_docs
            ]

            return documents, total


# Create singleton instance
document_service = DocumentService()
