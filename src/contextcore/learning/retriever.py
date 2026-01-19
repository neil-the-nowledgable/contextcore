"""Retrieve lessons from Tempo for agent work sessions.

This module provides the LessonRetriever class for querying lessons
stored in Tempo using TraceQL.
"""

__all__ = ["LessonRetriever"]

import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from contextcore.learning.models import (
    Lesson,
    LessonCategory,
    LessonQuery,
    LessonSource,
)


class LessonRetriever:
    """Query lessons from Tempo for agent work sessions.

    Example:
        retriever = LessonRetriever()

        # Get lessons for a specific file
        lessons = retriever.get_lessons_for_file(
            "src/auth/oauth.py",
            project_id="my-project"
        )

        # Get lessons for a task type
        lessons = retriever.get_lessons_for_task("testing")
    """

    def __init__(self, tempo_url: str = "http://localhost:3200") -> None:
        """Initialize the retriever.

        Args:
            tempo_url: URL of the Tempo instance
        """
        self.tempo_url = tempo_url.rstrip("/")

    def retrieve(self, query: LessonQuery) -> List[Lesson]:
        """Retrieve lessons matching query criteria.

        Args:
            query: Query parameters for filtering lessons

        Returns:
            List of matching lessons, sorted by effectiveness
        """
        # Build TraceQL query
        traceql = self._build_traceql(query)

        # Query Tempo
        raw_results = self._query_tempo(traceql, query.time_range)

        # Parse into Lesson objects
        lessons = self._parse_results(raw_results)

        # Filter by confidence
        lessons = [l for l in lessons if l.confidence >= query.min_confidence]

        # Sort by effectiveness
        lessons.sort(key=lambda l: l.effectiveness_score, reverse=True)

        return lessons[: query.max_results]

    def get_lessons_for_file(
        self,
        file_path: str,
        project_id: Optional[str] = None,
        category: Optional[LessonCategory] = None,
    ) -> List[Lesson]:
        """Get lessons applicable to a specific file.

        Args:
            file_path: Path to the file
            project_id: Optional project filter
            category: Optional category filter

        Returns:
            List of relevant lessons
        """
        query = LessonQuery(
            project_id=project_id,
            file_pattern=file_path,
            category=category,
            include_global=True,
        )
        return self.retrieve(query)

    def get_lessons_for_task(
        self,
        task_type: str,
        project_id: Optional[str] = None,
    ) -> List[Lesson]:
        """Get lessons applicable to a type of task.

        Args:
            task_type: Type of task (testing, debugging, refactoring, etc.)
            project_id: Optional project filter

        Returns:
            List of relevant lessons
        """
        # Map task type to likely categories
        category_mapping = {
            "testing": LessonCategory.TESTING,
            "debugging": LessonCategory.DEBUGGING,
            "refactoring": LessonCategory.REFACTORING,
            "security": LessonCategory.SECURITY,
            "performance": LessonCategory.PERFORMANCE,
            "deployment": LessonCategory.DEPLOYMENT,
            "documentation": LessonCategory.DOCUMENTATION,
            "architecture": LessonCategory.ARCHITECTURE,
            "integration": LessonCategory.INTEGRATION,
            "error_handling": LessonCategory.ERROR_HANDLING,
        }
        category = category_mapping.get(task_type.lower())

        query = LessonQuery(
            project_id=project_id,
            category=category,
            include_global=True,
        )
        return self.retrieve(query)

    def get_global_lessons(
        self,
        category: Optional[LessonCategory] = None,
        min_confidence: float = 0.9,
    ) -> List[Lesson]:
        """Get high-confidence global lessons.

        Args:
            category: Optional category filter
            min_confidence: Minimum confidence threshold

        Returns:
            List of global lessons
        """
        query = LessonQuery(
            project_id=None,
            category=category,
            min_confidence=min_confidence,
            include_global=True,
        )
        return self.retrieve(query)

    def get_recent_lessons(
        self,
        project_id: Optional[str] = None,
        hours: int = 24,
    ) -> List[Lesson]:
        """Get lessons created in the last N hours.

        Args:
            project_id: Optional project filter
            hours: Number of hours to look back

        Returns:
            List of recent lessons
        """
        query = LessonQuery(
            project_id=project_id,
            time_range=f"{hours}h",
            include_global=True,
            max_results=50,
        )
        return self.retrieve(query)

    def _build_traceql(self, query: LessonQuery) -> str:
        """Build TraceQL query from LessonQuery.

        Args:
            query: The query parameters

        Returns:
            TraceQL query string
        """
        conditions = ['span.insight.type = "lesson"']

        if query.project_id:
            if query.include_global:
                conditions.append(
                    f'(span.project.id = "{query.project_id}" || span.lesson.is_global = true)'
                )
            else:
                conditions.append(f'span.project.id = "{query.project_id}"')
        elif query.include_global:
            conditions.append("span.lesson.is_global = true")

        if query.category:
            conditions.append(f'span.lesson.category = "{query.category.value}"')

        if query.file_pattern:
            # Use regex matching for file patterns
            # Escape special regex characters except * and **
            pattern = query.file_pattern
            pattern = pattern.replace(".", "\\.")
            pattern = pattern.replace("**", ".*")
            pattern = pattern.replace("*", "[^/]*")
            conditions.append(f'span.lesson.applies_to =~ ".*{pattern}.*"')

        return "{ " + " && ".join(conditions) + " }"

    def _query_tempo(self, traceql: str, time_range: str) -> List[Dict[str, Any]]:
        """Execute TraceQL query against Tempo.

        Args:
            traceql: The TraceQL query string
            time_range: Time range string (e.g., "1h", "7d")

        Returns:
            List of trace dictionaries
        """
        # Parse time range
        duration = self._parse_time_range(time_range)
        end = datetime.now()
        start = end - duration

        params = {
            "q": traceql,
            "start": int(start.timestamp()),
            "end": int(end.timestamp()),
        }

        url = f"{self.tempo_url}/api/search?{urlencode(params)}"

        try:
            req = Request(url)
            req.add_header("Accept", "application/json")
            with urlopen(req, timeout=30) as response:
                data = json.loads(response.read())
                return data.get("traces", [])
        except URLError as e:
            print(f"[LessonRetriever] Query failed: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"[LessonRetriever] Failed to parse response: {e}")
            return []

    def _parse_results(self, raw_results: List[Dict[str, Any]]) -> List[Lesson]:
        """Parse raw Tempo results into Lesson objects.

        Args:
            raw_results: List of trace dictionaries from Tempo

        Returns:
            List of Lesson objects
        """
        lessons = []

        for trace_data in raw_results:
            # Handle different Tempo response formats
            spans = trace_data.get("spans", [])
            if not spans and "spanSets" in trace_data:
                for span_set in trace_data.get("spanSets", []):
                    spans.extend(span_set.get("spans", []))

            for span in spans:
                attrs = span.get("attributes", {})

                # Check if this is a lesson span
                if attrs.get("insight.type") != "lesson":
                    continue

                # Parse applies_to (stored as JSON string)
                applies_to_raw = attrs.get("lesson.applies_to", "[]")
                if isinstance(applies_to_raw, str):
                    try:
                        applies_to = json.loads(applies_to_raw)
                    except json.JSONDecodeError:
                        applies_to = []
                else:
                    applies_to = applies_to_raw if isinstance(applies_to_raw, list) else []

                # Parse category
                category_str = attrs.get("lesson.category", "debugging")
                try:
                    category = LessonCategory(category_str)
                except ValueError:
                    category = LessonCategory.DEBUGGING

                # Parse source
                source_str = attrs.get("lesson.source", "pattern_discovered")
                try:
                    source = LessonSource(source_str)
                except ValueError:
                    source = LessonSource.PATTERN_DISCOVERED

                lesson = Lesson(
                    id=attrs.get("lesson.id", ""),
                    summary=attrs.get("lesson.summary", ""),
                    category=category,
                    source=source,
                    applies_to=applies_to,
                    project_id=attrs.get("project.id"),
                    confidence=float(attrs.get("lesson.confidence", 0.5)),
                    context=attrs.get("lesson.context", ""),
                    code_example=attrs.get("lesson.code_example"),
                    anti_pattern=attrs.get("lesson.anti_pattern"),
                    agent_id=attrs.get("agent.id", ""),
                    trace_id=trace_data.get("traceId", ""),
                )
                lessons.append(lesson)

        return lessons

    def _parse_time_range(self, time_range: str) -> timedelta:
        """Parse time range string to timedelta.

        Args:
            time_range: Time range string (e.g., "1h", "7d", "30d", "1m")

        Returns:
            Corresponding timedelta
        """
        match = re.match(r"(\d+)([hdwm])", time_range)
        if not match:
            return timedelta(days=7)  # Default

        value = int(match.group(1))
        unit = match.group(2)

        units = {
            "h": timedelta(hours=value),
            "d": timedelta(days=value),
            "w": timedelta(weeks=value),
            "m": timedelta(days=value * 30),
        }
        return units.get(unit, timedelta(days=7))
