"""
Prompt management system for AI interactions.

This module provides a templating system for AI prompts with support for:
- Variable substitution in templates
- Role-based messaging (system, user, assistant)
- Management of prompt collections for different tasks
- Version tracking for prompt templates
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PromptRole(str, Enum):
    """Role types for chat-based AI systems."""

    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'


@dataclass
class PromptMessage:
    """A single message in a multi-message prompt."""

    role: PromptRole
    content: str
    name: str | None = None


@dataclass
class PromptTemplate:
    """
    Template for AI prompts with variable substitution.

    Example:
        template = PromptTemplate(
            name="document_analysis",
            description="Analyze document content",
            version="1.0",
            template_messages=[
                PromptMessage(
                    role=PromptRole.SYSTEM,
                    content="You are an expert document analyzer. "
                           "Analyze the following {document_type} document."
                ),
                PromptMessage(
                    role=PromptRole.USER,
                    content="Document content: {content}"
                )
            ]
        )

        formatted = template.format(
            document_type="academic",
            content="This research paper..."
        )
    """

    name: str
    description: str
    version: str = '1.0'
    template_messages: list[PromptMessage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def format(self, **kwargs) -> list[dict[str, str]]:
        """
        Format the prompt by substituting variables in the template.

        Args:
            **kwargs: Variables to substitute in the template.

        Returns:
            list[dict[str, str]]: List of formatted messages ready for AI API.
        """
        formatted_messages = []

        for msg in self.template_messages:
            content = msg.content

            # Substitute variables using both {var} and basic string formatting
            # First find all variables in the template
            var_pattern = r'\{([a-zA-Z0-9_]+)\}'
            variables = re.findall(var_pattern, content)

            # Check if all required variables are provided
            missing_vars = [var for var in variables if var not in kwargs]
            if missing_vars:
                missing_vars_str = ', '.join(missing_vars)
                raise ValueError(f'Missing required variables: {missing_vars_str}')

            # Perform substitution
            formatted_content = content.format(**kwargs)

            message_dict = {'role': msg.role, 'content': formatted_content}

            if msg.name:
                message_dict['name'] = msg.name

            formatted_messages.append(message_dict)

        return formatted_messages

    def format_single_prompt(self, **kwargs) -> str:
        """
        Format and combine all messages into a single prompt string.
        Useful for non-chat based AI interfaces.

        Args:
            **kwargs: Variables to substitute in the template.

        Returns:
            str: Combined prompt with role indicators.
        """
        formatted_parts = []

        for msg in self.template_messages:
            content = msg.content

            # Substitute variables
            for key, value in kwargs.items():
                content = content.replace(f'{{{key}}}', str(value))

            # Format with role prefix
            if msg.role == PromptRole.SYSTEM:
                formatted_parts.append(f'[System]: {content}')
            elif msg.role == PromptRole.USER:
                formatted_parts.append(f'[User]: {content}')
            elif msg.role == PromptRole.ASSISTANT:
                formatted_parts.append(f'[Assistant]: {content}')

        return '\n\n'.join(formatted_parts)


class PromptLibrary:
    """
    Collection of prompt templates organized by categories.
    """

    def __init__(self):
        self._templates: dict[str, PromptTemplate] = {}

    def add_template(self, template: PromptTemplate) -> None:
        """Add a template to the library."""
        key = f'{template.name}_v{template.version}'
        self._templates[key] = template

    def get_template(self, name: str, version: str | None = None) -> PromptTemplate:
        """
        Get a template by name and optionally version.

        Args:
            name: Template name
            version: Specific version to retrieve. If None, returns the latest version.

        Returns:
            PromptTemplate: The requested template

        Raises:
            KeyError: If template doesn't exist
        """
        if version:
            key = f'{name}_v{version}'
            if key not in self._templates:
                raise KeyError(f"Template '{name}' with version '{version}' not found")
            return self._templates[key]

        # Find latest version
        matching_templates = [
            (k, v) for k, v in self._templates.items() if k.startswith(f'{name}_v')
        ]

        if not matching_templates:
            raise KeyError(f"No template named '{name}' found")

        # Sort by version and return the latest
        latest_template = sorted(
            matching_templates, key=lambda x: x[1].version, reverse=True
        )[0][1]

        return latest_template

    def list_templates(self) -> list[dict[str, str]]:
        """List all available templates with their versions."""
        return [
            {
                'name': template.name,
                'version': template.version,
                'description': template.description,
            }
            for template in self._templates.values()
        ]


# Create a global prompt library instance
prompt_library = PromptLibrary()


# Document analysis template
DOCUMENT_ANALYSIS_SYSTEM_CONTENT = (
    'You are an expert teaching assistant specialized in analyzing educational '
    'materials. Extract key information from the following {document_type} document. '
    'Focus on main topics, key concepts, difficulty level, and suggested learning'
    'outcomes.'
)

# Image analysis template
IMAGE_ANALYSIS_SYSTEM_CONTENT = (
    'You are a teaching assistant with expertise in visual content analysis. '
    'Analyze the described image and identify educational concepts, topics, '
    'and potential teaching applications.'
)

# Question generation template
QUESTION_GEN_SYSTEM_CONTENT = (
    'You are an assessment specialist who creates high-quality educational questions. '
    'Generate {question_count} {question_type} questions about {topic} at '
    '{difficulty_level} level. Each question should test understanding of key '
    'concepts and include correct answers.'
)


# Initialize with default templates
def _initialize_default_templates():
    """Initialize the global prompt library with default templates."""

    # Document analysis template
    document_analysis = PromptTemplate(
        name='document_analysis',
        description='Analyze document content and extract key information',
        version='1.0',
        template_messages=[
            PromptMessage(
                role=PromptRole.SYSTEM, content=DOCUMENT_ANALYSIS_SYSTEM_CONTENT
            ),
            PromptMessage(role=PromptRole.USER, content='Document content: {content}'),
        ],
        metadata={
            'required_fields': ['document_type', 'content'],
            'output_format': 'text',
        },
    )

    # Image analysis template
    image_analysis = PromptTemplate(
        name='image_analysis',
        description='Analyze image content for educational relevance',
        version='1.0',
        template_messages=[
            PromptMessage(
                role=PromptRole.SYSTEM, content=IMAGE_ANALYSIS_SYSTEM_CONTENT
            ),
            PromptMessage(
                role=PromptRole.USER, content='Image description: {image_description}'
            ),
        ],
        metadata={'required_fields': ['image_description'], 'output_format': 'text'},
    )

    # Question generation template
    question_generation = PromptTemplate(
        name='question_generation',
        description='Generate educational questions based on content',
        version='1.0',
        template_messages=[
            PromptMessage(
                role=PromptRole.SYSTEM,
                content=QUESTION_GEN_SYSTEM_CONTENT,
            ),
            PromptMessage(
                role=PromptRole.USER,
                content='Content for question generation: {content}',
            ),
        ],
        metadata={
            'required_fields': [
                'question_count',
                'question_type',
                'topic',
                'difficulty_level',
                'content',
            ],
            'question_types': [
                'multiple-choice',
                'short-answer',
                'essay',
                'true-false',
            ],
            'difficulty_levels': [
                'elementary',
                'middle-school',
                'high-school',
                'college',
                'advanced',
            ],
        },
    )

    # Add templates to library
    prompt_library.add_template(document_analysis)
    prompt_library.add_template(image_analysis)
    prompt_library.add_template(question_generation)


# Initialize default templates
_initialize_default_templates()
