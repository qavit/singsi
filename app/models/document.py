from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    Integer,
    String,
    Text,
)

from app.db.base_class import Base


class DocumentType(str, Enum):
    """Document types supported by the system."""

    PDF = 'pdf'
    WORD = 'docx'
    TEXT = 'txt'
    IMAGE = 'image'
    MARKDOWN = 'md'


class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents."""

    title: str
    description: str | None = None
    subject: str | None = None
    grade_level: str | None = None
    tags: list[str] = Field(default_factory=list)
    language: str = 'zh-TW'

    model_config = {
        'extra': 'allow',
    }


class Document(BaseModel):
    """Document model with content and metadata."""

    id: str = Field(default_factory=lambda: f'doc_{int(datetime.now().timestamp())}')
    filename: str
    content_type: str
    file_size: int
    type: DocumentType
    metadata: DocumentMetadata
    storage_path: str | None = None  # Add this field
    vector_ids: list[str] = Field(default_factory=list)  # For vector store references
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    analysis_results: dict[str, Any] = Field(default_factory=dict)


class DocumentDB(Base):
    """SQLAlchemy model for document storage."""

    __tablename__ = 'documents'

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    type = Column(SAEnum(DocumentType), nullable=False)
    doc_metadata = Column(
        Text, nullable=False
    )  # Changed from 'metadata' to 'doc_metadata'
    storage_path = Column(String)
    vector_ids = Column(Text)  # JSON array
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    analysis_results = Column(Text)  # JSON string
