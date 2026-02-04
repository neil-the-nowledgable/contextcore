"""
Tests for deliverable validation in TaskTracker.

Validates that:
- Tasks without deliverables complete normally (backward compat)
- Tasks with passing deliverables record verification success
- Tasks with failing deliverables warn but still complete
- File-type deliverables auto-check os.path.exists
- Custom validators are called and their results recorded
- Validator exceptions are handled gracefully
"""

import json
import os
import tempfile

import pytest
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from contextcore.tracker import (
    TaskTracker,
    Deliverable,
    DeliverableResult,
    TASK_DELIVERABLE_COUNT,
    TASK_DELIVERABLE_VERIFIED,
    TASK_DELIVERABLES_COMPLETE,
    TASK_STATUS,
    TASK_PERCENT_COMPLETE,
)
from contextcore.contracts.types import TaskStatus


class CollectingExporter(SpanExporter):
    """Collects spans in memory for testing."""

    def __init__(self):
        self.spans = []

    def export(self, spans):
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis=30000):
        return True


@pytest.fixture
def temp_state_dir():
    """Create a temporary directory for state persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def exporter():
    """Create a collecting exporter for testing."""
    return CollectingExporter()


@pytest.fixture
def tracker(temp_state_dir, exporter):
    """Create a TaskTracker with test configuration."""
    return TaskTracker(
        project="test-project",
        service_name="test-service",
        state_dir=temp_state_dir,
        exporter=exporter,
    )


class TestBackwardCompatibility:
    """Ensure existing behavior is preserved when no deliverables are specified."""

    def test_complete_task_no_deliverables(self, tracker, exporter):
        """Completing a task without deliverables should work as before."""
        tracker.start_task(task_id="COMPAT-1", title="No deliverables")
        tracker.complete_task("COMPAT-1")

        assert "COMPAT-1" not in tracker.get_active_tasks()

    def test_complete_task_no_deliverables_sets_done(self, tracker, exporter):
        """Task without deliverables should have DONE status."""
        tracker.start_task(task_id="COMPAT-2", title="Done check")
        tracker.complete_task("COMPAT-2")
        tracker.shutdown()

        span = exporter.spans[-1]
        assert span.attributes[TASK_STATUS] == TaskStatus.DONE.value
        assert span.attributes[TASK_PERCENT_COMPLETE] == 100.0

    def test_no_deliverables_verified_event_without_deliverables(self, tracker, exporter):
        """No deliverables_verified event should be emitted without deliverables."""
        tracker.start_task(task_id="COMPAT-3", title="No event")
        tracker.complete_task("COMPAT-3")
        tracker.shutdown()

        span = exporter.spans[-1]
        event_names = [e.name for e in span.events]
        assert "task.deliverables_verified" not in event_names
        assert "task.completed" in event_names


class TestPassingDeliverables:
    """Test deliverable validation when all deliverables pass."""

    def test_file_deliverable_exists(self, tracker, exporter):
        """File deliverable should pass when file exists."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            temp_path = f.name
            f.write(b"test content")

        try:
            deliverables = [
                Deliverable(
                    type="file",
                    path=temp_path,
                    description="Test output file",
                ),
            ]
            tracker.start_task(
                task_id="PASS-1",
                title="File exists",
                deliverables=deliverables,
            )
            tracker.complete_task("PASS-1")
            tracker.shutdown()

            span = exporter.spans[-1]
            assert span.attributes[TASK_STATUS] == TaskStatus.DONE.value
            assert span.attributes[TASK_DELIVERABLES_COMPLETE] is True
            assert span.attributes[TASK_DELIVERABLE_COUNT] == 1
            assert span.attributes[TASK_DELIVERABLE_VERIFIED] == 1

            # Check the verification event
            verified_events = [
                e for e in span.events if e.name == "task.deliverables_verified"
            ]
            assert len(verified_events) == 1
            event = verified_events[0]
            assert event.attributes["deliverable.count"] == 1
            assert event.attributes["deliverable.verified_count"] == 1
            assert event.attributes["deliverable.failed_count"] == 0
        finally:
            os.unlink(temp_path)

    def test_custom_validator_passes(self, tracker, exporter):
        """Custom validator returning True should mark deliverable as verified."""
        deliverables = [
            Deliverable(
                type="api",
                path="https://api.example.com/health",
                description="API health check",
                validator=lambda: True,
            ),
        ]
        tracker.start_task(
            task_id="PASS-2",
            title="Custom validator passes",
            deliverables=deliverables,
        )
        tracker.complete_task("PASS-2")
        tracker.shutdown()

        span = exporter.spans[-1]
        assert span.attributes[TASK_DELIVERABLES_COMPLETE] is True
        assert span.attributes[TASK_DELIVERABLE_VERIFIED] == 1

    def test_multiple_deliverables_all_pass(self, tracker, exporter):
        """All deliverables passing should set deliverables_complete=True."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            temp_path = f.name
            f.write(b"# code")

        try:
            deliverables = [
                Deliverable(
                    type="file",
                    path=temp_path,
                    description="Source file",
                ),
                Deliverable(
                    type="test",
                    path="tests/test_foo.py",
                    description="Test passes",
                    validator=lambda: True,
                ),
                Deliverable(
                    type="config",
                    path="config.yaml",
                    description="Config exists",
                    validator=lambda: True,
                ),
            ]
            tracker.start_task(
                task_id="PASS-3",
                title="Multiple pass",
                deliverables=deliverables,
            )
            tracker.complete_task("PASS-3")
            tracker.shutdown()

            span = exporter.spans[-1]
            assert span.attributes[TASK_DELIVERABLE_COUNT] == 3
            assert span.attributes[TASK_DELIVERABLE_VERIFIED] == 3
            assert span.attributes[TASK_DELIVERABLES_COMPLETE] is True
        finally:
            os.unlink(temp_path)

    def test_non_file_without_validator_passes(self, tracker, exporter):
        """Non-file deliverable without a validator should be treated as verified."""
        deliverables = [
            Deliverable(
                type="section",
                path="docs/README.md#overview",
                description="Overview section",
            ),
        ]
        tracker.start_task(
            task_id="PASS-4",
            title="No validator non-file",
            deliverables=deliverables,
        )
        tracker.complete_task("PASS-4")
        tracker.shutdown()

        span = exporter.spans[-1]
        assert span.attributes[TASK_DELIVERABLES_COMPLETE] is True
        assert span.attributes[TASK_DELIVERABLE_VERIFIED] == 1


class TestFailingDeliverables:
    """Test deliverable validation when some or all deliverables fail."""

    def test_file_deliverable_missing(self, tracker, exporter):
        """File deliverable should fail when file does not exist."""
        deliverables = [
            Deliverable(
                type="file",
                path="/nonexistent/path/to/file.txt",
                description="Expected output",
            ),
        ]
        tracker.start_task(
            task_id="FAIL-1",
            title="Missing file",
            deliverables=deliverables,
        )
        tracker.complete_task("FAIL-1")

        # Task should still complete despite failed deliverable
        assert "FAIL-1" not in tracker.get_active_tasks()

        tracker.shutdown()
        span = exporter.spans[-1]
        assert span.attributes[TASK_STATUS] == TaskStatus.DONE.value
        assert span.attributes[TASK_PERCENT_COMPLETE] == 100.0
        assert span.attributes[TASK_DELIVERABLES_COMPLETE] is False
        assert span.attributes[TASK_DELIVERABLE_VERIFIED] == 0

    def test_custom_validator_returns_false(self, tracker, exporter):
        """Custom validator returning False should mark deliverable as failed."""
        deliverables = [
            Deliverable(
                type="test",
                path="tests/test_integration.py",
                description="Integration tests pass",
                validator=lambda: False,
            ),
        ]
        tracker.start_task(
            task_id="FAIL-2",
            title="Validator fails",
            deliverables=deliverables,
        )
        tracker.complete_task("FAIL-2")
        tracker.shutdown()

        span = exporter.spans[-1]
        assert span.attributes[TASK_DELIVERABLES_COMPLETE] is False
        assert span.attributes[TASK_DELIVERABLE_VERIFIED] == 0

        # Verify the event contains failure details
        verified_events = [
            e for e in span.events if e.name == "task.deliverables_verified"
        ]
        assert len(verified_events) == 1
        event = verified_events[0]
        assert event.attributes["deliverable.failed_count"] == 1

        results = json.loads(event.attributes["deliverable.results"])
        assert len(results) == 1
        assert results[0]["verified"] is False
        assert "Custom validator returned False" in results[0]["reason"]

    def test_validator_raises_exception(self, tracker, exporter):
        """Validator that raises exception should fail gracefully."""

        def bad_validator():
            raise RuntimeError("Connection refused")

        deliverables = [
            Deliverable(
                type="api",
                path="https://api.example.com/status",
                description="API reachable",
                validator=bad_validator,
            ),
        ]
        tracker.start_task(
            task_id="FAIL-3",
            title="Validator exception",
            deliverables=deliverables,
        )
        tracker.complete_task("FAIL-3")
        tracker.shutdown()

        span = exporter.spans[-1]
        # Task still completes
        assert span.attributes[TASK_STATUS] == TaskStatus.DONE.value
        assert span.attributes[TASK_DELIVERABLES_COMPLETE] is False

        verified_events = [
            e for e in span.events if e.name == "task.deliverables_verified"
        ]
        results = json.loads(verified_events[0].attributes["deliverable.results"])
        assert "RuntimeError" in results[0]["reason"]
        assert "Connection refused" in results[0]["reason"]

    def test_mixed_pass_and_fail(self, tracker, exporter):
        """Mix of passing and failing deliverables should record partial results."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            existing_path = f.name
            f.write(b"data")

        try:
            deliverables = [
                Deliverable(
                    type="file",
                    path=existing_path,
                    description="Existing file",
                ),
                Deliverable(
                    type="file",
                    path="/does/not/exist.txt",
                    description="Missing file",
                ),
                Deliverable(
                    type="test",
                    path="tests/test_smoke.py",
                    description="Smoke test",
                    validator=lambda: True,
                ),
            ]
            tracker.start_task(
                task_id="FAIL-4",
                title="Mixed results",
                deliverables=deliverables,
            )
            tracker.complete_task("FAIL-4")
            tracker.shutdown()

            span = exporter.spans[-1]
            assert span.attributes[TASK_STATUS] == TaskStatus.DONE.value
            assert span.attributes[TASK_DELIVERABLE_COUNT] == 3
            assert span.attributes[TASK_DELIVERABLE_VERIFIED] == 2
            assert span.attributes[TASK_DELIVERABLES_COMPLETE] is False

            verified_events = [
                e for e in span.events if e.name == "task.deliverables_verified"
            ]
            event = verified_events[0]
            assert event.attributes["deliverable.verified_count"] == 2
            assert event.attributes["deliverable.failed_count"] == 1
        finally:
            os.unlink(existing_path)

    def test_failing_deliverables_still_complete(self, tracker, exporter):
        """Task with ALL failing deliverables should still complete (warn-only)."""
        deliverables = [
            Deliverable(
                type="file",
                path="/no/such/file1.py",
                description="Output 1",
            ),
            Deliverable(
                type="file",
                path="/no/such/file2.py",
                description="Output 2",
            ),
        ]
        tracker.start_task(
            task_id="FAIL-5",
            title="All fail",
            deliverables=deliverables,
        )
        tracker.complete_task("FAIL-5")

        # Key: task is NOT in active spans (it completed)
        assert "FAIL-5" not in tracker.get_active_tasks()

        tracker.shutdown()
        span = exporter.spans[-1]
        assert span.attributes[TASK_STATUS] == TaskStatus.DONE.value


class TestDeliverableResultsJson:
    """Test the JSON results payload in the span event."""

    def test_results_json_structure(self, tracker, exporter):
        """The deliverable.results event attribute should contain valid JSON."""
        deliverables = [
            Deliverable(
                type="file",
                path="/tmp/test_output.txt",
                description="Test output file",
                validator=lambda: True,
            ),
        ]
        tracker.start_task(
            task_id="JSON-1",
            title="JSON structure",
            deliverables=deliverables,
        )
        tracker.complete_task("JSON-1")
        tracker.shutdown()

        span = exporter.spans[-1]
        verified_events = [
            e for e in span.events if e.name == "task.deliverables_verified"
        ]
        results_json = verified_events[0].attributes["deliverable.results"]

        # Should be valid JSON
        results = json.loads(results_json)
        assert isinstance(results, list)
        assert len(results) == 1

        entry = results[0]
        assert entry["type"] == "file"
        assert entry["path"] == "/tmp/test_output.txt"
        assert entry["description"] == "Test output file"
        assert entry["verified"] is True
        assert entry["reason"] is None


class TestDeliverableCleanup:
    """Test that deliverable state is cleaned up after completion."""

    def test_deliverables_removed_after_complete(self, tracker, exporter):
        """Deliverables should be cleaned up from internal state after completion."""
        deliverables = [
            Deliverable(type="file", path="/tmp/x.txt", description="X"),
        ]
        tracker.start_task(
            task_id="CLEAN-1",
            title="Cleanup test",
            deliverables=deliverables,
        )

        # Deliverables should exist before completion
        assert "CLEAN-1" in tracker._task_deliverables

        tracker.complete_task("CLEAN-1")

        # Deliverables should be cleaned up
        assert "CLEAN-1" not in tracker._task_deliverables

    def test_no_deliverables_no_cleanup_needed(self, tracker, exporter):
        """Tasks without deliverables should not leave residual state."""
        tracker.start_task(task_id="CLEAN-2", title="No deliverables")
        assert "CLEAN-2" not in tracker._task_deliverables

        tracker.complete_task("CLEAN-2")
        assert "CLEAN-2" not in tracker._task_deliverables


class TestDeliverableDataclass:
    """Test the Deliverable and DeliverableResult dataclasses."""

    def test_deliverable_creation(self):
        """Deliverable should be constructable with required fields."""
        d = Deliverable(
            type="file",
            path="/tmp/output.py",
            description="Generated Python module",
        )
        assert d.type == "file"
        assert d.path == "/tmp/output.py"
        assert d.description == "Generated Python module"
        assert d.validator is None

    def test_deliverable_with_validator(self):
        """Deliverable should accept an optional validator callable."""
        check = lambda: True
        d = Deliverable(
            type="api",
            path="https://api.example.com",
            description="API endpoint",
            validator=check,
        )
        assert d.validator is check
        assert d.validator() is True

    def test_deliverable_result_creation(self):
        """DeliverableResult should capture verification outcome."""
        d = Deliverable(type="file", path="/tmp/x.txt", description="Test")
        result = DeliverableResult(deliverable=d, verified=False, reason="Not found")
        assert result.verified is False
        assert result.reason == "Not found"
        assert result.deliverable is d

    def test_deliverable_result_defaults(self):
        """DeliverableResult reason should default to None."""
        d = Deliverable(type="file", path="/tmp/x.txt", description="Test")
        result = DeliverableResult(deliverable=d, verified=True)
        assert result.reason is None


class TestWarningLogging:
    """Test that warnings are logged for failed deliverables."""

    def test_warning_logged_for_failed_deliverable(self, tracker, exporter, caplog):
        """Failed deliverables should produce a warning log message."""
        import logging

        deliverables = [
            Deliverable(
                type="file",
                path="/nonexistent/file.txt",
                description="Missing output",
            ),
        ]
        tracker.start_task(
            task_id="LOG-1",
            title="Log warning test",
            deliverables=deliverables,
        )

        with caplog.at_level(logging.WARNING, logger="contextcore.tracker"):
            tracker.complete_task("LOG-1")

        # Check that a warning was logged
        warning_messages = [
            r.message for r in caplog.records if r.levelno == logging.WARNING
        ]
        assert any("LOG-1" in msg and "failed verification" in msg for msg in warning_messages)
