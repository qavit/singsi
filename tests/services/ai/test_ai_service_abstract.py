"""Tests for the AIService abstract interface."""

from abc import ABC

import pytest

from app.services.ai.base import AIService


def test_ai_service_is_abstract():
    """Test that AIService is an abstract base class."""
    assert issubclass(AIService, ABC)

    # Verify abstract methods exist
    abstract_methods = [
        'analyze_document',
        'generate_response',
        'analyze_image',
        'generate_image',
    ]

    for method in abstract_methods:
        assert hasattr(AIService, method)
        # Check if the method is abstract
        method_obj = getattr(AIService, method)
        assert getattr(method_obj, '__isabstractmethod__', False)

    # Ensure we can't instantiate the abstract class
    with pytest.raises(TypeError):
        AIService()
