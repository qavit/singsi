from abc import ABC, abstractmethod
from typing import Any


class AIService(ABC):
    """Interface for AI powered operations."""

    @abstractmethod
    def analyze_document(self, document: str) -> dict[str, Any]:
        """Analyze the document and return analysis result."""
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a response based on the provided prompt."""
        pass

    @abstractmethod
    def analyze_image(self, image_path: str) -> dict[str, Any]:
        """Analyze an image and return analysis result."""
        pass

    @abstractmethod
    def generate_image(self, prompt: str) -> Any:
        """Generate an image based on the provided prompt."""
        pass
