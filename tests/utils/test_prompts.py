"""Tests for the prompts utility module."""

import pytest

from app.utils.prompts import PromptLibrary, PromptMessage, PromptRole, PromptTemplate

# Constant values for testing
TEST_ROLE = 'teacher'
TEST_CONTENT = 'sample text'
ANALYZE_TEMPLATE_NAME = 'analyze'
VERSION_1 = '1.0'
VERSION_2 = '2.0'
DOCUMENT_ANALYSIS_TEMPLATE = 'document_analysis'
PDF_TYPE = 'PDF'
MATH_CONTENT = 'This document discusses mathematics.'
MIN_EXPECTED_TEMPLATES = 3


def test_prompt_template_basic():
    """Test basic prompt template functionality."""
    # Define test input messages
    system_message = PromptMessage(role=PromptRole.SYSTEM, content='You are a {role}.')
    user_message = PromptMessage(
        role=PromptRole.USER, content='Process this: {content}'
    )
    test_messages = [system_message, user_message]

    template = PromptTemplate(
        name='test',
        description='Test template',
        template_messages=test_messages,
    )

    # Test formatting
    formatted = template.format(role=TEST_ROLE, content=TEST_CONTENT)

    # Verify the output matches input structure
    expected_message_count = len(test_messages)
    assert len(formatted) == expected_message_count

    assert formatted[0]['role'] == 'system'
    assert formatted[0]['content'] == f'You are a {TEST_ROLE}.'
    assert formatted[1]['content'] == f'Process this: {TEST_CONTENT}'

    # Test missing variable error
    with pytest.raises(ValueError):
        template.format(role=TEST_ROLE)  # Missing 'content'


def test_prompt_template_single_format():
    """Test single string formatting."""
    # Define test messages
    test_messages = [
        PromptMessage(role=PromptRole.SYSTEM, content='You are a {role}.'),
        PromptMessage(role=PromptRole.USER, content='Process this: {content}'),
    ]

    template = PromptTemplate(
        name='test',
        description='Test template',
        template_messages=test_messages,
    )

    result = template.format_single_prompt(role=TEST_ROLE, content=TEST_CONTENT)
    assert f'[System]: You are a {TEST_ROLE}.' in result
    assert f'[User]: Process this: {TEST_CONTENT}' in result


def test_prompt_library():
    """Test prompt library functionality."""
    library = PromptLibrary()

    # Add templates with different versions
    template_v1 = PromptTemplate(
        name=ANALYZE_TEMPLATE_NAME,
        description='Analysis template v1',
        version=VERSION_1,
        template_messages=[
            PromptMessage(role=PromptRole.SYSTEM, content='Analyze: {content}')
        ],
    )

    template_v2 = PromptTemplate(
        name=ANALYZE_TEMPLATE_NAME,
        description='Analysis template v2',
        version=VERSION_2,
        template_messages=[
            PromptMessage(
                role=PromptRole.SYSTEM, content='Analyze thoroughly: {content}'
            )
        ],
    )

    library.add_template(template_v1)
    library.add_template(template_v2)

    # Expected number of templates after adding
    expected_template_count = 2

    # Test getting specific version
    result = library.get_template(ANALYZE_TEMPLATE_NAME, version=VERSION_1)
    assert result.version == VERSION_1
    assert 'Analyze: {content}' in result.template_messages[0].content

    # Test getting latest version
    result = library.get_template(ANALYZE_TEMPLATE_NAME)
    assert result.version == VERSION_2
    assert 'Analyze thoroughly: {content}' in result.template_messages[0].content

    # Test listing templates
    templates = library.list_templates()
    assert len(templates) == expected_template_count
    assert any(
        t['name'] == ANALYZE_TEMPLATE_NAME and t['version'] == VERSION_1
        for t in templates
    )
    assert any(
        t['name'] == ANALYZE_TEMPLATE_NAME and t['version'] == VERSION_2
        for t in templates
    )


def test_global_prompt_library():
    """Test the global prompt library instance."""
    from app.utils.prompts import prompt_library

    # Check that default templates are loaded
    templates = prompt_library.list_templates()
    assert len(templates) >= MIN_EXPECTED_TEMPLATES

    # Try getting a specific template
    document_template = prompt_library.get_template(DOCUMENT_ANALYSIS_TEMPLATE)
    assert document_template.name == DOCUMENT_ANALYSIS_TEMPLATE
    assert 'document_type' in document_template.template_messages[0].content

    # Test formatting a default template
    messages = document_template.format(document_type=PDF_TYPE, content=MATH_CONTENT)
    expected_message_count = len(document_template.template_messages)
    assert len(messages) == expected_message_count

    assert PDF_TYPE in messages[0]['content']
    assert MATH_CONTENT in messages[1]['content']
