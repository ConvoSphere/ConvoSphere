"""
Assistant Processor Service.

This module provides processing logic for assistant requests,
including request validation, preprocessing, and post-processing.
"""

from typing import Any

from loguru import logger

from backend.app.schemas.hybrid_mode import ConversationMode


class ProcessingRequest:
    """Request for message processing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ProcessingResult:
    """Result of message processing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class AssistantProcessor:
    """Processor for assistant request handling and validation."""

    def __init__(self):
        """Initialize the processor."""

    async def validate_request(
        self, request: ProcessingRequest
    ) -> tuple[bool, str | None]:
        """
        Validate processing request.

        Args:
            request: Processing request

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Check required fields
            if not request.user_id:
                return False, "User ID is required"

            if not request.conversation_id:
                return False, "Conversation ID is required"

            if not request.message or not request.message.strip():
                return False, "Message content is required"

            # Validate message length
            if len(request.message) > 10000:
                return False, "Message too long (max 10000 characters)"

            # Validate temperature
            if request.temperature < 0.0 or request.temperature > 2.0:
                return False, "Temperature must be between 0.0 and 2.0"

            # Validate max tokens
            if request.max_tokens and request.max_tokens < 1:
                return False, "Max tokens must be at least 1"

            # Validate max context chunks
            if request.max_context_chunks < 1 or request.max_context_chunks > 50:
                return False, "Max context chunks must be between 1 and 50"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    async def preprocess_request(self, request: ProcessingRequest) -> ProcessingRequest:
        """
        Preprocess the request.

        Args:
            request: Processing request

        Returns:
            ProcessingRequest: Preprocessed request
        """
        try:
            # Clean message content
            request.message = request.message.strip()

            # Set default values if not provided
            if request.temperature is None:
                request.temperature = 0.7

            if request.max_tokens is None:
                request.max_tokens = 2048

            if request.max_context_chunks is None:
                request.max_context_chunks = 5

            if request.metadata is None:
                request.metadata = {}

            # Add preprocessing metadata
            request.metadata["preprocessed"] = True
            request.metadata["original_message_length"] = len(request.message)

            logger.debug(
                f"Preprocessed request for conversation {request.conversation_id}"
            )
            return request

        except Exception as e:
            logger.error(f"Error preprocessing request: {e}")
            return request

    async def postprocess_result(self, result: ProcessingResult) -> ProcessingResult:
        """
        Postprocess the result.

        Args:
            result: Processing result

        Returns:
            ProcessingResult: Postprocessed result
        """
        try:
            # Add postprocessing metadata
            result.metadata["postprocessed"] = True
            result.metadata["final_content_length"] = len(result.content)

            # Validate response content
            if result.success and result.content:
                # Basic content validation
                if len(result.content) > 50000:
                    result.content = result.content[:50000] + "..."
                    result.metadata["content_truncated"] = True

                # Check for potential issues
                if (
                    "error" in result.content.lower()
                    or "exception" in result.content.lower()
                ):
                    result.metadata["potential_issues"] = True

            logger.debug(f"Postprocessed result for request {result.request_id}")
            return result

        except Exception as e:
            logger.error(f"Error postprocessing result: {e}")
            return result

    async def analyze_request_complexity(
        self, request: ProcessingRequest
    ) -> dict[str, Any]:
        """
        Analyze request complexity.

        Args:
            request: Processing request

        Returns:
            dict: Complexity analysis
        """
        try:
            message = request.message
            complexity_score = 0.0

            # Analyze message length
            word_count = len(message.split())
            if word_count < 10:
                complexity_score += 0.2
            elif word_count < 30:
                complexity_score += 0.5
            elif word_count < 60:
                complexity_score += 0.7
            else:
                complexity_score += 0.9

            # Analyze for complex keywords
            complex_keywords = [
                "analyze",
                "compare",
                "research",
                "investigate",
                "calculate",
                "compute",
                "generate",
                "create",
                "build",
                "develop",
                "implement",
                "optimize",
                "debug",
                "test",
                "validate",
                "verify",
                "synthesize",
                "integrate",
            ]

            found_keywords = []
            for keyword in complex_keywords:
                if keyword.lower() in message.lower():
                    found_keywords.append(keyword)
                    complexity_score += 0.1

            # Analyze for multi-step indicators
            step_indicators = [
                "first",
                "then",
                "next",
                "finally",
                "after",
                "before",
                "step",
                "phase",
                "stage",
            ]

            step_count = 0
            for indicator in step_indicators:
                if indicator.lower() in message.lower():
                    step_count += 1

            if step_count > 0:
                complexity_score += min(0.3, step_count * 0.1)

            # Cap complexity score
            complexity_score = min(1.0, complexity_score)

            return {
                "complexity_score": round(complexity_score, 2),
                "word_count": word_count,
                "complex_keywords": found_keywords,
                "step_indicators": step_count,
                "complexity_level": self._get_complexity_level(complexity_score),
            }

        except Exception as e:
            logger.error(f"Error analyzing request complexity: {e}")
            return {"error": str(e)}

    def _get_complexity_level(self, score: float) -> str:
        """Get complexity level based on score."""
        if score < 0.3:
            return "simple"
        elif score < 0.6:
            return "moderate"
        elif score < 0.8:
            return "complex"
        else:
            return "very_complex"

    async def suggest_processing_mode(
        self, request: ProcessingRequest, complexity_analysis: dict[str, Any]
    ) -> ConversationMode:
        """
        Suggest processing mode based on request analysis.

        Args:
            request: Processing request
            complexity_analysis: Complexity analysis

        Returns:
            ConversationMode: Suggested processing mode
        """
        try:
            complexity_score = complexity_analysis.get("complexity_score", 0.5)
            word_count = complexity_analysis.get("word_count", 0)
            complex_keywords = complexity_analysis.get("complex_keywords", [])

            # Simple rules for mode suggestion
            if complexity_score > 0.7 or len(complex_keywords) > 2:
                return ConversationMode.AGENT
            elif complexity_score < 0.3 and word_count < 20:
                return ConversationMode.CHAT
            else:
                return ConversationMode.AUTO

        except Exception as e:
            logger.error(f"Error suggesting processing mode: {e}")
            return ConversationMode.AUTO

    async def extract_request_intent(
        self, request: ProcessingRequest
    ) -> dict[str, Any]:
        """
        Extract intent from the request.

        Args:
            request: Processing request

        Returns:
            dict: Intent analysis
        """
        try:
            message = request.message.lower()
            intent = {
                "primary_intent": "general",
                "confidence": 0.5,
                "intents": [],
            }

            # Define intent patterns
            intent_patterns = {
                "question": [
                    "was",
                    "wie",
                    "wann",
                    "wo",
                    "warum",
                    "wer",
                    "which",
                    "what",
                    "when",
                    "where",
                    "why",
                    "who",
                    "how",
                ],
                "calculation": [
                    "berechnen",
                    "rechnen",
                    "calculate",
                    "compute",
                    "math",
                    "sum",
                    "multiply",
                    "divide",
                ],
                "search": [
                    "suchen",
                    "finden",
                    "search",
                    "find",
                    "lookup",
                    "recherchieren",
                ],
                "analysis": [
                    "analysieren",
                    "analyze",
                    "auswerten",
                    "evaluate",
                    "examine",
                ],
                "creation": ["erstellen", "create", "generate", "build", "make"],
                "help": ["hilfe", "help", "support", "assist"],
            }

            # Check for intent patterns
            for intent_name, patterns in intent_patterns.items():
                for pattern in patterns:
                    if pattern in message:
                        intent["intents"].append(intent_name)
                        intent["confidence"] += 0.2

            # Set primary intent
            if intent["intents"]:
                intent["primary_intent"] = intent["intents"][0]
                intent["confidence"] = min(1.0, intent["confidence"])

            return intent

        except Exception as e:
            logger.error(f"Error extracting request intent: {e}")
            return {"primary_intent": "general", "confidence": 0.5, "intents": []}

    def get_processor_stats(self) -> dict[str, Any]:
        """
        Get processor statistics.

        Returns:
            dict: Processor statistics
        """
        try:
            return {
                "processor_type": "assistant_processor",
                "version": "1.0.0",
                "capabilities": [
                    "request_validation",
                    "request_preprocessing",
                    "result_postprocessing",
                    "complexity_analysis",
                    "intent_extraction",
                    "mode_suggestion",
                ],
            }

        except Exception as e:
            logger.error(f"Error getting processor stats: {e}")
            return {"error": str(e)}


# Global processor instance
assistant_processor = AssistantProcessor()
