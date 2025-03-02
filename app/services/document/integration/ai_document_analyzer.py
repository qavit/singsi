"""AI-enhanced document analysis integration module."""

import logging
from typing import Any

from app.services.ai.base.ai_service_abstract import AIService
from app.services.document.education_content_analyzer import (
    EducationalContentAnalyzer,
)
from app.services.document.parser_base import ParsingResult

logger = logging.getLogger(__name__)


class AIDocumentAnalyzer:
    """Analyzer that combines document parsing with AI-enhanced analysis."""

    def __init__(self, ai_service: AIService):
        """
        Initialize the AI document analyzer.

        Args:
            ai_service: AI service for content analysis
        """
        self.ai_service = ai_service
        self.edu_analyzer = EducationalContentAnalyzer(ai_service)

    async def analyze_document(
        self, parsing_result: ParsingResult, analysis_depth: str = 'standard'
    ) -> dict[str, Any]:
        """
        Analyze a document with AI assistance.

        Args:
            parsing_result: The parsed document result
            analysis_depth: Level of analysis ("basic", "standard", or "deep")

        Returns:
            Analysis results as a dictionary
        """
        logger.info(f'Performing {analysis_depth} analysis on document')

        # First use the educational content analyzer
        edu_analysis = await self.edu_analyzer.analyze(parsing_result)

        # Perform additional AI analysis based on depth
        ai_enhancement = await self._perform_depth_specific_analysis(
            parsing_result, edu_analysis, analysis_depth
        )

        # Combine all analyses
        result = {
            'document_type': edu_analysis.get('document_type', 'unknown'),
            'structure': parsing_result.structure,
            'educational_elements': edu_analysis.get('educational_elements', {}),
            'ai_insights': ai_enhancement,
        }

        # For deep analysis, add relationship mapping
        if analysis_depth == 'deep' and not parsing_result.error:
            try:
                relationships = await self._analyze_content_relationships(
                    parsing_result.text, edu_analysis
                )
                result['content_relationships'] = relationships
            except Exception as e:
                logger.error(f'Failed to analyze content relationships: {e}')
                result['errors'] = [
                    *result.get('errors', []),
                    'Relationship analysis failed',
                ]

        return result

    async def _perform_depth_specific_analysis(
        self, parsing_result: ParsingResult, edu_analysis: dict[str, Any], depth: str
    ) -> dict[str, Any]:
        """
        Perform analysis specific to the requested depth.

        Args:
            parsing_result: The parsed document
            edu_analysis: Educational analysis results
            depth: Analysis depth level

        Returns:
            Depth-specific analysis results
        """
        document_type = edu_analysis.get('document_type', 'unknown')

        if depth == 'basic':
            # Basic analysis is minimal
            return await self._get_basic_analysis(parsing_result.text, document_type)

        elif depth == 'deep':
            # Deep analysis includes more comprehensive insights
            return await self._get_deep_analysis(
                parsing_result.text, document_type, edu_analysis
            )

        # Standard analysis (default)
        return await self._get_standard_analysis(
            parsing_result.text, document_type, edu_analysis
        )

    async def _get_basic_analysis(self, text: str, doc_type: str) -> dict[str, Any]:
        """Perform basic document analysis."""
        prompt = f"""
        Provide a basic analysis of the following {doc_type} document.
        Focus only on:
        1. Main topic or subject
        2. Target audience level
        3. 3-5 key points

        Return as JSON with fields: main_topic, audience_level, key_points

        Content:
        {text[:2000]}  # Using shorter text for basic analysis
        """

        try:
            response = await self.ai_service.complete_prompt(prompt)
            import json

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {'summary': response}
        except Exception as e:
            logger.error(f'Basic analysis failed: {e}')
            return {'error': str(e)}

    async def _get_standard_analysis(
        self, text: str, doc_type: str, edu_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform standard document analysis."""
        # Create a prompt based on document type and existing analysis
        edu_analysis.get('educational_elements', {})

        prompt = f"""
        Analyze the following {doc_type} document in standard depth.
        Focus on:
        1. Comprehensive subject matter identification
        2. Educational value assessment
        3. Knowledge points and learning objectives
        4. Teaching/learning recommendations
        5. Content quality evaluation

        Return as JSON with fields: subject_matter, educational_value, knowledge_points,
         recommendations, content_quality_score (1-5)

        Content:
        {text[:3500]}
        """

        try:
            response = await self.ai_service.complete_prompt(prompt)
            import json

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {'analysis': response}
        except Exception as e:
            logger.error(f'Standard analysis failed: {e}')
            return {'error': str(e)}

    async def _get_deep_analysis(
        self, text: str, doc_type: str, edu_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform deep document analysis."""
        # More comprehensive analysis with specific focus based on document type
        prompt = f"""
        Perform deep analysis on the following {doc_type} document.
        Include:
        1. Detailed subject matter mapping
        2. Pedagogical approach assessment
        3. Bloom's taxonomy classification of content
        4. Detailed strengths and weaknesses
        5. Enhancement suggestions with specific examples
        6. Academic standards alignment
        7. Alternative approaches or perspectives

        Return as JSON with appropriate fields for each section above.

        Content:
        {text[:4000]}
        """

        try:
            response = await self.ai_service.complete_prompt(prompt)
            import json

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {'detailed_analysis': response}
        except Exception as e:
            logger.error(f'Deep analysis failed: {e}')
            return {'error': str(e)}

    async def _analyze_content_relationships(
        self, text: str, edu_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze relationships between content elements."""
        # Extract concepts and analyze their relationships
        prompt = """
        Analyze the relationships between key concepts in the document.
        Create a knowledge graph structure showing:
        1. Main concepts
        2. Relationships between concepts (prerequisite, related, builds-upon)
        3. Conceptual hierarchy or dependency

        Return as JSON with fields: nodes (concepts), edges (relationships)

        Content:
        {text[:3500]}
        """

        try:
            response = await self.ai_service.complete_prompt(prompt)
            import json

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {'relationship_map': 'Could not structure relationship data'}
        except Exception as e:
            logger.error(f'Relationship analysis failed: {e}')
            return {'error': str(e)}
