"""Emit lessons as OpenTelemetry spans for storage in Tempo.

This module provides the LessonEmitter class for persisting lessons
learned during agent work sessions.
"""

__all__ = ["LessonEmitter"]

import json
from datetime import datetime
from typing import List, Optional

from opentelemetry import trace
from opentelemetry.trace import SpanKind

from contextcore.learning.models import (
    Lesson,
    LessonCategory,
    LessonSource,
)


class LessonEmitter:
    """Emit lessons as OTel spans for storage and retrieval.

    Example:
        emitter = LessonEmitter(project_id="my-project", agent_id="claude")

        # Emit a lesson
        lesson = emitter.emit_lesson(
            summary="Always mock external APIs in unit tests",
            category=LessonCategory.TESTING,
            source=LessonSource.BLOCKER_RESOLVED,
            applies_to=["tests/**/*.py"],
            confidence=0.9,
        )

        # Record that the lesson was applied
        emitter.record_application(lesson.id, success=True, context="test_auth.py")
    """

    def __init__(
        self,
        project_id: str,
        agent_id: str,
        session_id: Optional[str] = None,
    ) -> None:
        """Initialize the lesson emitter.

        Args:
            project_id: The project this emitter is associated with
            agent_id: Identifier for the agent emitting lessons
            session_id: Optional session identifier
        """
        self.project_id = project_id
        self.agent_id = agent_id
        self.session_id = session_id or f"session-{datetime.now().timestamp()}"
        self._tracer = trace.get_tracer("contextcore.learning")

    def emit_lesson(
        self,
        summary: str,
        category: LessonCategory,
        source: LessonSource,
        applies_to: List[str],
        confidence: float = 0.8,
        context: str = "",
        code_example: Optional[str] = None,
        anti_pattern: Optional[str] = None,
        global_lesson: bool = False,
    ) -> Lesson:
        """Emit a lesson learned during agent work.

        Args:
            summary: Brief description of the lesson (1-2 sentences)
            category: Category for organization/filtering
            source: How this lesson was learned
            applies_to: File patterns where this lesson applies
            confidence: How confident agent is in this lesson (0.0-1.0)
            context: Extended description/explanation
            code_example: Example code demonstrating the lesson
            anti_pattern: Example of what NOT to do
            global_lesson: If True, applies to all projects

        Returns:
            The created Lesson object
        """
        lesson_id = f"lesson-{datetime.now().timestamp()}"
        trace_id = ""

        # Create span with lesson attributes
        with self._tracer.start_as_current_span(
            name="lesson.emit",
            kind=SpanKind.INTERNAL,
        ) as span:
            # Core identification
            span.set_attribute("insight.type", "lesson")
            span.set_attribute("lesson.id", lesson_id)
            span.set_attribute("lesson.summary", summary)

            # Classification
            span.set_attribute("lesson.category", category.value)
            span.set_attribute("lesson.source", source.value)

            # Scope
            span.set_attribute("lesson.applies_to", json.dumps(applies_to))
            if not global_lesson:
                span.set_attribute("project.id", self.project_id)
            span.set_attribute("lesson.is_global", global_lesson)

            # Confidence
            span.set_attribute("lesson.confidence", confidence)

            # Content
            if context:
                span.set_attribute("lesson.context", context)
            if code_example:
                span.set_attribute("lesson.code_example", code_example)
            if anti_pattern:
                span.set_attribute("lesson.anti_pattern", anti_pattern)

            # Agent context
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("agent.session_id", self.session_id)

            # Add event for searchability
            span.add_event(
                "lesson_created",
                attributes={
                    "category": category.value,
                    "applies_to_count": len(applies_to),
                },
            )

            # Capture trace ID
            span_context = span.get_span_context()
            if span_context:
                trace_id = format(span_context.trace_id, "032x")

        lesson = Lesson(
            id=lesson_id,
            summary=summary,
            category=category,
            source=source,
            applies_to=applies_to,
            project_id=None if global_lesson else self.project_id,
            confidence=confidence,
            context=context,
            code_example=code_example,
            anti_pattern=anti_pattern,
            agent_id=self.agent_id,
            trace_id=trace_id,
        )

        return lesson

    def emit_blocker_resolution(
        self,
        blocker_summary: str,
        resolution: str,
        applies_to: List[str],
        confidence: float = 0.9,
    ) -> Lesson:
        """Convenience method for lessons learned from resolving blockers.

        Args:
            blocker_summary: What the blocker was
            resolution: How it was resolved
            applies_to: File patterns this applies to
            confidence: Confidence in the lesson

        Returns:
            The created Lesson object
        """
        return self.emit_lesson(
            summary=f"Resolved: {blocker_summary}",
            category=LessonCategory.DEBUGGING,
            source=LessonSource.BLOCKER_RESOLVED,
            applies_to=applies_to,
            confidence=confidence,
            context=resolution,
        )

    def emit_pattern_discovery(
        self,
        pattern_name: str,
        description: str,
        applies_to: List[str],
        code_example: str,
        anti_pattern: Optional[str] = None,
    ) -> Lesson:
        """Convenience method for pattern discoveries.

        Args:
            pattern_name: Name of the discovered pattern
            description: Description of the pattern
            applies_to: File patterns this applies to
            code_example: Example code showing the pattern
            anti_pattern: Example of what NOT to do

        Returns:
            The created Lesson object
        """
        return self.emit_lesson(
            summary=f"Pattern: {pattern_name}",
            category=LessonCategory.ARCHITECTURE,
            source=LessonSource.PATTERN_DISCOVERED,
            applies_to=applies_to,
            confidence=0.85,
            context=description,
            code_example=code_example,
            anti_pattern=anti_pattern,
        )

    def emit_error_fix(
        self,
        error_type: str,
        fix_description: str,
        applies_to: List[str],
        code_example: Optional[str] = None,
    ) -> Lesson:
        """Convenience method for lessons from fixing errors.

        Args:
            error_type: Type of error that was fixed
            fix_description: How the error was fixed
            applies_to: File patterns this applies to
            code_example: Example code showing the fix

        Returns:
            The created Lesson object
        """
        return self.emit_lesson(
            summary=f"Fix for {error_type}",
            category=LessonCategory.ERROR_HANDLING,
            source=LessonSource.ERROR_FIXED,
            applies_to=applies_to,
            confidence=0.9,
            context=fix_description,
            code_example=code_example,
        )

    def emit_human_guidance(
        self,
        guidance: str,
        category: LessonCategory,
        applies_to: List[str],
        context: str = "",
        global_lesson: bool = False,
    ) -> Lesson:
        """Convenience method for lessons from human guidance.

        Args:
            guidance: The guidance provided
            category: Category for the lesson
            applies_to: File patterns this applies to
            context: Additional context
            global_lesson: Whether this applies globally

        Returns:
            The created Lesson object
        """
        return self.emit_lesson(
            summary=guidance,
            category=category,
            source=LessonSource.HUMAN_GUIDANCE,
            applies_to=applies_to,
            confidence=1.0,  # Human guidance is trusted
            context=context,
            global_lesson=global_lesson,
        )

    def record_application(
        self,
        lesson_id: str,
        success: bool,
        context: str,
        feedback: Optional[str] = None,
    ) -> None:
        """Record that a lesson was applied (for effectiveness tracking).

        Args:
            lesson_id: ID of the lesson that was applied
            success: Whether applying the lesson was successful
            context: Where/how the lesson was applied
            feedback: Optional feedback about the application
        """
        with self._tracer.start_as_current_span(
            name="lesson.applied",
            kind=SpanKind.INTERNAL,
        ) as span:
            span.set_attribute("lesson.id", lesson_id)
            span.set_attribute("lesson.applied", True)
            span.set_attribute("lesson.success", success)
            span.set_attribute("lesson.application_context", context)
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("agent.session_id", self.session_id)
            if feedback:
                span.set_attribute("lesson.feedback", feedback)

            span.add_event(
                "lesson_applied",
                attributes={
                    "success": success,
                },
            )
