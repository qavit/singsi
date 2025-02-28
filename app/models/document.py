from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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
    vector_ids: list[str] = Field(default_factory=list)  # For vector store references
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    analysis_results: dict[str, Any] = Field(default_factory=dict)
