"""Data models for agent learning system.

This module defines the data models for storing and retrieving lessons
learned during agent work sessions.
"""

__all__ = [
    "LessonCategory",
    "LessonSource",
    "Lesson",
    "LessonQuery",
    "LessonApplication",
]

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class LessonCategory(Enum):
    """Categories for organizing lessons."""

    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DEBUGGING = "debugging"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    ERROR_HANDLING = "error_handling"
    INTEGRATION = "integration"


class LessonSource(Enum):
    """How the lesson was learned."""

    BLOCKER_RESOLVED = "blocker_resolved"
    ERROR_FIXED = "error_fixed"
    PATTERN_DISCOVERED = "pattern_discovered"
    REVIEW_FEEDBACK = "review_feedback"
    HUMAN_GUIDANCE = "human_guidance"
    DOCUMENTATION = "documentation"


@dataclass
class Lesson:
    """A single lesson learned by an agent.

    Attributes:
        id: Unique identifier for the lesson
        summary: Brief description (1-2 sentences)
        category: Category for organization/filtering
        source: How this lesson was learned
        applies_to: File patterns where this lesson applies
        project_id: Specific project, or None for global lessons
        confidence: How confident agent is in this lesson (0.0-1.0)
        validated_by_human: Whether a human has validated this lesson
        success_count: Times this lesson was applied successfully
        failure_count: Times this lesson didn't help
        context: Extended description/explanation
        code_example: Example code demonstrating the lesson
        anti_pattern: Example of what NOT to do
        agent_id: ID of the agent that created this lesson
        trace_id: OpenTelemetry trace ID for this lesson
        created_at: When the lesson was created
        expires_at: When the lesson should be considered stale
    """

    id: str
    summary: str
    category: LessonCategory
    source: LessonSource
    applies_to: List[str]
    project_id: Optional[str] = None
    confidence: float = 0.8
    validated_by_human: bool = False
    success_count: int = 0
    failure_count: int = 0
    context: str = ""
    code_example: Optional[str] = None
    anti_pattern: Optional[str] = None
    agent_id: str = ""
    trace_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    @property
    def effectiveness_score(self) -> float:
        """Calculate lesson effectiveness based on usage.

        Returns:
            Effectiveness score between 0.0 and 1.0
        """
        total = self.success_count + self.failure_count
        if total == 0:
            return self.confidence
        return (self.success_count / total) * self.confidence

    @property
    def is_global(self) -> bool:
        """Check if this is a global lesson.

        Returns:
            True if lesson applies to all projects
        """
        return self.project_id is None

    def to_dict(self) -> Dict[str, Any]:
        """Convert lesson to a serializable dictionary.

        Returns:
            Dictionary representation of the lesson
        """
        return {
            "id": self.id,
            "summary": self.summary,
            "category": self.category.value,
            "source": self.source.value,
            "applies_to": self.applies_to,
            "project_id": self.project_id,
            "confidence": self.confidence,
            "validated_by_human": self.validated_by_human,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "context": self.context,
            "code_example": self.code_example,
            "anti_pattern": self.anti_pattern,
            "agent_id": self.agent_id,
            "trace_id": self.trace_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "effectiveness_score": self.effectiveness_score,
            "is_global": self.is_global,
        }


@dataclass
class LessonQuery:
    """Query parameters for retrieving lessons.

    Attributes:
        project_id: Filter by project ID
        file_pattern: Filter by file pattern
        category: Filter by category
        min_confidence: Minimum confidence threshold
        include_global: Whether to include global lessons
        max_results: Maximum number of results to return
        time_range: Time range for lessons (e.g., "1h", "7d", "30d")
    """

    project_id: Optional[str] = None
    file_pattern: Optional[str] = None
    category: Optional[LessonCategory] = None
    min_confidence: float = 0.5
    include_global: bool = True
    max_results: int = 10
    time_range: str = "30d"


@dataclass
class LessonApplication:
    """Record of applying a lesson.

    Attributes:
        lesson_id: ID of the lesson that was applied
        applied_at: When the lesson was applied
        context: Where/how the lesson was applied
        success: Whether applying the lesson was successful
        feedback: Optional feedback about the application
    """

    lesson_id: str
    applied_at: datetime
    context: str
    success: bool
    feedback: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a serializable dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "lesson_id": self.lesson_id,
            "applied_at": self.applied_at.isoformat(),
            "context": self.context,
            "success": self.success,
            "feedback": self.feedback,
        }
