from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Base class for AI service providers."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize AI model and resources."""
        pass

    @abstractmethod
    async def process_text(
        self, text: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Process text with AI model."""
        pass

    @abstractmethod
    async def analyze_document(
        self,
        content: bytes,
        filename: str,
        content_type: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze uploaded document content."""
        pass
