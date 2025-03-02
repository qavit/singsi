"""Educational Content Analyzer

Extracts and classifies educational features from parsed documents
"""

import logging
from enum import Enum
from typing import Any

from app.services.ai.base.ai_service_abstract import AIService
from app.services.document.parser_base import ParsingResult


class EducationalDocumentType(Enum):
    """Educational document type enumeration"""

    UNKNOWN = 'unknown'
    SYLLABUS = 'syllabus'
    LECTURE_NOTES = 'lecture_notes'
    WORKSHEET = 'worksheet'
    EXAM = 'exam'
    TEXTBOOK = 'textbook'
    LESSON_PLAN = 'lesson_plan'


class EducationalContentAnalyzer:
    """
    Educational content analyzer for analyzing and classifying educational document
    structures
    """

    def __init__(self, ai_service: AIService | None = None):
        """
        Initialize the educational content analyzer

        Args:
            ai_service: Optional AI service for enhanced content analysis
        """
        self.ai_service = ai_service
        self._initialize_patterns()
        self.logger = logging.getLogger(__name__)

    def _initialize_patterns(self) -> None:
        """Initialize patterns used to identify educational content elements"""
        # These patterns can be expanded based on actual requirements
        self.patterns = {
            # Regular expressions for identifying question numbers
            'question_number': [
                r'^\s*(\d+[\.)。])',  # 1. or 1。
                r'^\s*([一二三四五六七八九十]+[\.)。])',  # Chinese numerals: 一.
                r'^\s*([IVXLCDM]+[\.)。])',  # Roman numerals: I. II. etc.
                r'^\s*第\s*(\d+)\s*題',  # Question #1 (Chinese)
            ],
            # Keywords for identifying learning objectives
            'learning_objectives': [
                'learning objectives',
                'teaching objectives',
                'course objectives',
                'students will be able to',
                'learning outcomes',
                'this course aims to',
                'learning focus',
                'core competencies',
                # Traditional Chinese equivalents
                '學習目標',
                '教學目標',
                '課程目標',
                '學生將能夠',
                '學習成果',
                '本課程旨在',
                '學習重點',
                '核心能力',
            ],
            # Keywords for identifying assessment criteria
            'assessment_criteria': [
                'assessment criteria',
                'grading criteria',
                'assessment methods',
                'grade calculation',
                'evaluation',
                # Traditional Chinese equivalents
                '評量標準',
                '評分標準',
                '評量方式',
                '成績計算',
                '學習評量',
            ],
        }

    async def analyze(self, parsing_result: ParsingResult) -> dict[str, Any]:
        """
        Analyze document parsing results, extract educational features

        Args:
            parsing_result: Document parsing result

        Returns:
            Dictionary containing educational content analysis
        """
        result = {
            'document_type': EducationalDocumentType.UNKNOWN.value,
            'educational_elements': {},
            'structure_analysis': {},
        }

        # Basic document type identification
        doc_type = self._identify_document_type(parsing_result)
        result['document_type'] = doc_type.value

        # Perform specific analysis based on document type
        if doc_type == EducationalDocumentType.WORKSHEET:
            result['educational_elements']['questions'] = self._extract_questions(
                parsing_result
            )
        elif doc_type == EducationalDocumentType.SYLLABUS:
            result['educational_elements'][
                'objectives'
            ] = self._extract_learning_objectives(parsing_result)

        # If AI service is available, use it to enhance analysis
        if self.ai_service:
            try:
                ai_analysis = await self._enhance_with_ai(parsing_result, doc_type)
                result['ai_enhanced_analysis'] = ai_analysis
            except Exception as e:
                self.logger.error(f'AI enhanced analysis failed: {e}')
                result['ai_analysis_error'] = str(e)

        return result

    def _identify_document_type(
        self, parsing_result: ParsingResult
    ) -> EducationalDocumentType:
        """
        Identify educational document type

        Args:
            parsing_result: Document parsing result

        Returns:
            Educational document type enumeration
        """
        text = parsing_result.text.lower()
        metadata = parsing_result.metadata

        # Log metadata for debugging purposes
        self.logger.debug(f'Document metadata: {metadata}')

        # Use heuristic rules to identify document type
        document_type = EducationalDocumentType.UNKNOWN

        if any(
            term in text
            for term in ['syllabus', 'course outline', '課程大綱', '教學大綱']
        ):
            document_type = EducationalDocumentType.SYLLABUS
        elif any(term in text for term in ['exam', 'quiz', 'test', '考試', '測驗']):
            document_type = EducationalDocumentType.EXAM
        elif any(term in text for term in ['worksheet', 'exercise', '練習', '作業']):
            document_type = EducationalDocumentType.WORKSHEET
        elif any(
            term in text
            for term in ['lesson plan', 'teaching plan', '教案', '課程計劃']
        ):
            document_type = EducationalDocumentType.LESSON_PLAN
        elif any(term in text for term in ['lecture', 'lecture notes', '講義']):
            document_type = EducationalDocumentType.LECTURE_NOTES
        elif self._contains_multiple_questions(text):
            # Further differentiate between worksheet and exam
            if any(
                term in text
                for term in ['grade', 'score', 'time limit', '評分', '成績', '時間限制']
            ):
                document_type = EducationalDocumentType.EXAM
            else:
                document_type = EducationalDocumentType.WORKSHEET

        return document_type

    def _contains_multiple_questions(self, text: str) -> bool:
        """Check if text contains multiple questions"""
        # Simple implementation, actual use would require more complex logic
        question_count = 0
        QUESTION_COUNT_THRESHOLD = 3
        lines = text.split('\n')

        for line in lines:
            for pattern in self.patterns['question_number']:
                import re

                if re.match(pattern, line):
                    question_count += 1
                    if (
                        question_count >= QUESTION_COUNT_THRESHOLD
                    ):  # Assume 3+ question numbers indicate an exercise or exam
                        return True

        return False

    def _extract_questions(self, parsing_result: ParsingResult) -> list[dict[str, Any]]:
        """Extract questions from document"""
        questions = []
        # Question extraction logic implementation
        # This is a simple example; actual implementation would require more complex
        # logic
        text = parsing_result.text
        lines = text.split('\n')

        current_question = None

        for line in lines:
            # Check if this is the start of a new question
            is_new_question = False
            for pattern in self.patterns['question_number']:
                import re

                match = re.match(pattern, line)
                if match:
                    # If there's a current question, save it
                    if current_question:
                        questions.append(current_question)

                    # Start new question
                    current_question = {
                        'number': match.group(1),
                        'text': line[match.end() :].strip(),
                        'options': [],
                        'sub_questions': [],
                    }
                    is_new_question = True
                    break

            # If not a new question and there's a current question, add this line to it
            if not is_new_question and current_question:
                # Check if this is an option
                option_match = re.match(r'^\s*([A-D])[\.、](.*)$', line)
                if option_match:
                    current_question['options'].append(
                        {
                            'label': option_match.group(1),
                            'text': option_match.group(2).strip(),
                        }
                    )
                # Add to question text
                elif line.strip():
                    current_question['text'] += '\n' + line.strip()

        # Don't forget to add the last question
        if current_question:
            questions.append(current_question)

        return questions

    def _extract_learning_objectives(self, parsing_result: ParsingResult) -> list[str]:
        """Extract learning objectives from syllabus"""
        objectives = []
        text = parsing_result.text

        # Find learning objectives section
        for objective_keyword in self.patterns['learning_objectives']:
            if objective_keyword in text:
                # Simple implementation: get text after the keyword
                start_pos = text.find(objective_keyword) + len(objective_keyword)
                # Find the start of the next paragraph or section
                end_pos = text.find('\n\n', start_pos)
                if end_pos == -1:
                    end_pos = len(text)

                objective_text = text[start_pos:end_pos].strip()
                # Split objective text into individual items
                if objective_text:
                    # Split by list items
                    import re

                    items = re.split(r'\n\s*[\d\.\)、]', objective_text)
                    for item in items:
                        if item.strip():
                            objectives.append(item.strip())

                break

        return objectives

    async def _enhance_with_ai(
        self, parsing_result: ParsingResult, doc_type: EducationalDocumentType
    ) -> dict[str, Any]:
        """
        Use AI service to enhance content analysis

        Args:
            parsing_result: Document parsing result
            doc_type: Identified document type

        Returns:
            AI-enhanced analysis results
        """
        if not self.ai_service:
            return {'error': 'AI service unavailable'}

        # Prepare different prompts based on document type
        if doc_type == EducationalDocumentType.SYLLABUS:
            prompt = self._get_syllabus_analysis_prompt(parsing_result.text)
        elif doc_type == EducationalDocumentType.WORKSHEET:
            prompt = self._get_worksheet_analysis_prompt(parsing_result.text)
        elif doc_type == EducationalDocumentType.EXAM:
            prompt = self._get_exam_analysis_prompt(parsing_result.text)
        else:
            prompt = self._get_general_education_analysis_prompt(parsing_result.text)

        try:
            # Call AI service
            response = await self.ai_service.complete_prompt(prompt)

            # Parse AI response (assuming it returns a JSON string)
            import json

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If not valid JSON, return raw response
                return {'raw_response': response}

        except Exception as e:
            self.logger.error(f'AI service call failed: {e}')
            return {'error': str(e)}

    def _get_general_education_analysis_prompt(self, text: str) -> str:
        """Generate general educational content analysis prompt"""
        return f"""
        Analyze the following educational document content and return results in JSON format: 
        1. Determine document type (syllabus, lecture notes, worksheet, exam, textbook, etc.)
        2. Extract main educational objectives or key points
        3. Identify key concepts and terminology
        4. Determine appropriate educational level (elementary, middle school, high school, university)
        
        Please return the results in JSON format with the following fields:
        - document_type: Document type
        - educational_level: Educational level
        - key_concepts: List of key concepts
        - main_objectives: List of main objectives
        
        Educational document content:
        {text[:4000]}  # Limit length to meet API requirements
        """  # noqa: E501

    def _get_syllabus_analysis_prompt(self, text: str) -> str:
        """Generate syllabus analysis prompt"""
        return f"""
        Analyze the following syllabus and return results in JSON format:
        1. Extract basic course information (course name, instructor, credits, etc.)
        2. Extract learning objectives
        3. Organize course outline/weekly topics
        4. Extract grading criteria and assignment requirements
        
        Please return the results in JSON format with the following fields:
        - course_info: Basic course information
        - learning_objectives: List of learning objectives
        - weekly_schedule: Weekly topics and content
        - assessment: Assessment methods and criteria
        
        Syllabus content:
        {text[:4000]}
        """

    def _get_worksheet_analysis_prompt(self, text: str) -> str:
        """Generate worksheet analysis prompt"""
        return f"""
        Analyze the following worksheet and return results in JSON format:
        1. Determine exercise topic and corresponding knowledge points
        2. Extract all questions and classify them (multiple choice, fill-in-blank, open-ended, etc.)
        3. Estimate difficulty level
        
        Please return the results in JSON format with the following fields:
        - topic: Exercise topic
        - knowledge_points: Related knowledge points
        - questions: List of questions, each with type, content, and options (if applicable)
        - difficulty_level: Difficulty assessment on scale of 1-5
        
        Worksheet content:
        {text[:4000]}
        """  # noqa: E501

    def _get_exam_analysis_prompt(self, text: str) -> str:
        """Generate exam analysis prompt"""
        return f"""
        Analyze the following exam paper and return results in JSON format:
        1. Identify exam subject and scope
        2. Extract all questions and their point values
        3. Identify question type distribution
        4. Estimate overall difficulty
        
        Please return the results in JSON format with the following fields:
        - exam_subject: Exam subject
        - exam_scope: Exam scope
        - total_points: Total points
        - question_distribution: Number and point values for different question types
        - questions: List of questions including type, point value, and content
        - difficulty_analysis: Difficulty analysis
        
        Exam content:
        {text[:4000]}
        """


# Create global instance for dependency injection
education_content_analyzer = EducationalContentAnalyzer()
