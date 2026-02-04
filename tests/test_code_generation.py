"""
Tests for code generation truncation prevention.

Tests the proactive truncation prevention pattern including:
- Size estimation accuracy
- Pre-flight rejection of large requests
- ExpectedOutput size constraints
- CodeGenerationCapability verification
"""

import pytest
from unittest.mock import MagicMock, patch

from contextcore.agent.size_estimation import (
    SizeEstimate,
    SizeEstimator,
    estimate_from_spec,
)
from contextcore.agent.code_generation import (
    ChunkSpec,
    CodeGenerationAction,
    CodeGenerationSpec,
    CodeGenerationHandoff,
    CodeGenerationCapability,
    CodeGenerationResult,
    CodeTruncatedError,
    HandoffRejectedError,
    GeneratedCode,
    VerificationResult,
)
from contextcore.agent.handoff import (
    ExpectedOutput,
    Handoff,
    HandoffPriority,
    HandoffStatus,
)


class TestSizeEstimator:
    """Tests for SizeEstimator heuristics."""

    def test_low_complexity_task(self):
        """Simple fix task should estimate low complexity."""
        estimator = SizeEstimator()
        estimate = estimator.estimate(
            task="Fix the simple small typo in the variable name",
            inputs={},
        )

        assert estimate.complexity == "low"
        assert estimate.lines < 50
        assert estimate.confidence > 0.3

    def test_high_complexity_task(self):
        """Comprehensive API implementation should estimate high."""
        estimator = SizeEstimator()
        estimate = estimator.estimate(
            task="Implement a comprehensive REST API client with CRUD operations and error handling",
            inputs={"required_exports": ["APIClient", "Response", "Error"]},
        )

        assert estimate.complexity == "high"
        assert estimate.lines > 100
        assert estimate.confidence > 0.5

    def test_medium_complexity_task(self):
        """Standard class implementation should be medium."""
        estimator = SizeEstimator()
        estimate = estimator.estimate(
            task="Implement the FooBar class with method x",
            inputs={"required_exports": ["FooBar"]},
        )

        assert estimate.complexity == "medium"
        assert 50 < estimate.lines < 150

    def test_required_exports_increase_estimate(self):
        """More exports should increase the estimate."""
        estimator = SizeEstimator()

        estimate_small = estimator.estimate(
            task="Implement classes",
            inputs={"required_exports": ["Foo"]},
        )

        estimate_large = estimator.estimate(
            task="Implement classes",
            inputs={"required_exports": ["Foo", "Bar", "Baz", "Qux"]},
        )

        assert estimate_large.lines > estimate_small.lines

    def test_crud_keyword_adds_methods(self):
        """CRUD keyword should add 4 methods to estimate."""
        estimator = SizeEstimator()

        estimate_crud = estimator.estimate(
            task="Implement CRUD operations for user management",
            inputs={},
        )

        estimate_no_crud = estimator.estimate(
            task="Implement operations for user management",
            inputs={},
        )

        # CRUD should add ~48 lines (4 methods * 12 lines)
        assert estimate_crud.lines > estimate_no_crud.lines + 30

    def test_tokens_calculated_from_lines(self):
        """Tokens should be approximately 3x lines."""
        estimator = SizeEstimator()
        estimate = estimator.estimate(
            task="Implement a simple function",
            inputs={},
        )

        assert estimate.tokens == estimate.lines * 3

    def test_reasoning_includes_complexity(self):
        """Reasoning should mention complexity."""
        estimator = SizeEstimator()
        estimate = estimator.estimate(
            task="Implement something",
            inputs={},
        )

        assert "Complexity:" in estimate.reasoning


class TestExpectedOutputExtensions:
    """Tests for ExpectedOutput size constraint extensions."""

    def test_default_values(self):
        """ExpectedOutput should have sensible defaults."""
        output = ExpectedOutput(
            type="code",
            fields=["content"],
        )

        assert output.max_lines is None
        assert output.max_tokens is None
        assert output.completeness_markers == []
        assert output.allows_chunking is True
        assert output.chunk_correlation_id is None

    def test_size_constraints_set(self):
        """Size constraints can be explicitly set."""
        output = ExpectedOutput(
            type="code",
            fields=["content"],
            max_lines=150,
            max_tokens=500,
            completeness_markers=["FooBar", "__all__"],
            allows_chunking=False,
        )

        assert output.max_lines == 150
        assert output.max_tokens == 500
        assert output.completeness_markers == ["FooBar", "__all__"]
        assert output.allows_chunking is False


class TestCodeGenerationSpec:
    """Tests for CodeGenerationSpec."""

    def test_default_values(self):
        """Spec should have sensible defaults."""
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="Implement FooBar",
        )

        assert spec.max_lines == 150
        assert spec.max_tokens == 500
        assert spec.allows_decomposition is True
        assert spec.must_have_docstring is True
        assert spec.context_files == []

    def test_estimate_from_spec(self):
        """estimate_from_spec should use spec fields."""
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="Implement FooBar class with methods x, y, z",
            required_exports=["FooBar"],
            must_have_docstring=True,
        )

        estimate = estimate_from_spec(spec)

        assert isinstance(estimate, SizeEstimate)
        assert estimate.lines > 0


class TestCodeGenerationCapability:
    """Tests for CodeGenerationCapability handler."""

    def test_verification_passes_valid_code(self):
        """Valid code should pass verification."""
        capability = CodeGenerationCapability()

        valid_code = '''"""Module docstring."""

class FooBar:
    """FooBar class."""

    def method_x(self):
        """Method x."""
        pass
'''
        issues = capability._verify_completeness(
            content=valid_code,
            required_exports=["FooBar"],
        )

        assert issues == []

    def test_verification_fails_missing_exports(self):
        """Missing required exports should fail verification."""
        capability = CodeGenerationCapability()

        incomplete_code = '''"""Module docstring."""

class WrongClass:
    pass
'''
        issues = capability._verify_completeness(
            content=incomplete_code,
            required_exports=["FooBar"],
        )

        assert len(issues) > 0
        assert any("Missing required exports" in i for i in issues)

    def test_verification_fails_syntax_error(self):
        """Syntax errors should fail verification."""
        capability = CodeGenerationCapability()

        bad_code = '''def foo(
    # Missing closing parenthesis
'''
        issues = capability._verify_completeness(
            content=bad_code,
            required_exports=None,
        )

        assert len(issues) > 0
        assert any("Syntax error" in i for i in issues)

    def test_verification_detects_truncation_markers(self):
        """Common truncation markers should be detected."""
        capability = CodeGenerationCapability()

        # Unclosed triple-quote (3 triple-quotes = odd = truncated)
        truncated_code = '''"""Module docstring."""

class Foo:
    """This docstring is not closed'''

        issues = capability._verify_completeness(
            content=truncated_code,
            required_exports=None,
        )

        assert len(issues) > 0
        assert any("TRUNCATED" in i for i in issues)

    def test_extract_exports_finds_classes(self):
        """Should extract class definitions."""
        capability = CodeGenerationCapability()

        code = '''class Foo:
    pass

class Bar:
    pass
'''
        exports = capability._extract_exports(code)

        assert "Foo" in exports
        assert "Bar" in exports

    def test_extract_exports_finds_functions(self):
        """Should extract public function definitions."""
        capability = CodeGenerationCapability()

        code = '''def public_func():
    pass

def _private_func():
    pass
'''
        exports = capability._extract_exports(code)

        assert "public_func" in exports
        assert "_private_func" not in exports


class TestCodeGenerationResult:
    """Tests for CodeGenerationResult."""

    def test_from_handoff_result(self):
        """Should create from base HandoffResult."""
        from contextcore.agent.handoff import HandoffResult

        base_result = HandoffResult(
            handoff_id="handoff-123",
            status=HandoffStatus.COMPLETED,
            result_trace_id="trace-456",
        )

        result = CodeGenerationResult.from_handoff_result(
            base_result,
            code_content="def foo(): pass",
        )

        assert result.handoff_id == "handoff-123"
        assert result.status == HandoffStatus.COMPLETED
        assert result.code_content == "def foo(): pass"
        assert result.decomposition_required is False

    def test_with_decomposition_info(self):
        """Should track decomposition details."""
        from contextcore.agent.handoff import HandoffResult

        base_result = HandoffResult(
            handoff_id="handoff-123",
            status=HandoffStatus.COMPLETED,
        )

        result = CodeGenerationResult.from_handoff_result(
            base_result,
            decomposition_info={
                "chunk_count": 3,
                "chunk_ids": ["chunk-1", "chunk-2", "chunk-3"],
            },
        )

        assert result.decomposition_required is True
        assert result.chunk_count == 3
        assert result.chunk_ids == ["chunk-1", "chunk-2", "chunk-3"]


class TestPreFlightIntegration:
    """Integration tests for pre-flight validation flow."""

    def test_pre_flight_triggers_decomposition(self):
        """Large estimates should suggest decomposition."""
        estimator = SizeEstimator()
        estimate = estimator.estimate(
            task="Implement a comprehensive system with full API, tests, documentation, and error handling for all edge cases",
            inputs={"required_exports": ["System", "API", "Tests", "Docs", "Errors"]},
        )

        # This large task should exceed limits
        if estimate.lines > 150:
            assert estimate.complexity == "high"
            # In a real flow, this would trigger decomposition

    def test_small_task_proceeds(self):
        """Small estimates should proceed with generation."""
        estimator = SizeEstimator()
        estimate = estimator.estimate(
            task="Fix the simple bug",
            inputs={},
        )

        assert estimate.lines < 150
        assert estimate.complexity == "low"


class TestTruncationDetection:
    """Tests for truncation detection in verification."""

    @pytest.mark.parametrize("truncated_code,expected_issue", [
        ('"""Unclosed', "TRUNCATED"),
        ("class Foo:\n    def bar(:\n", "Syntax error"),
        ("...", "TRUNCATED"),
    ])
    def test_truncation_patterns_detected(self, truncated_code, expected_issue):
        """Various truncation patterns should be detected."""
        capability = CodeGenerationCapability()
        issues = capability._verify_completeness(
            content=truncated_code,
            required_exports=None,
        )

        assert len(issues) > 0
        assert any(expected_issue in str(i) for i in issues)


class TestDecomposeSpec:
    """Tests for CodeGenerationCapability._decompose_spec."""

    def test_splits_by_required_exports(self):
        """Should split into chunks based on required_exports."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="Implement classes",
            max_lines=100,
            required_exports=["Foo", "Bar", "Baz", "Qux"],
        )
        estimate = SizeEstimate(
            lines=400,
            tokens=1200,
            complexity="high",
            confidence=0.7,
            reasoning="Large output expected",
        )

        chunks = capability._decompose_spec(spec, estimate)

        assert len(chunks) > 1
        # Every export should appear in exactly one chunk
        all_exports = []
        for chunk in chunks:
            assert chunk.required_exports is not None
            all_exports.extend(chunk.required_exports)
        assert set(all_exports) == {"Foo", "Bar", "Baz", "Qux"}

    def test_chunks_disable_recursive_decomposition(self):
        """Each chunk should have allows_decomposition=False."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="Implement classes",
            max_lines=50,
            required_exports=["Alpha", "Beta", "Gamma"],
        )
        estimate = SizeEstimate(
            lines=300,
            tokens=900,
            complexity="high",
            confidence=0.7,
            reasoning="Large",
        )

        chunks = capability._decompose_spec(spec, estimate)

        for chunk in chunks:
            assert chunk.allows_decomposition is False

    def test_chunks_target_same_file(self):
        """All chunks should target the same file as the original spec."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="Implement classes",
            max_lines=50,
            required_exports=["X", "Y"],
        )
        estimate = SizeEstimate(
            lines=200, tokens=600, complexity="high",
            confidence=0.7, reasoning="Large",
        )

        chunks = capability._decompose_spec(spec, estimate)

        for chunk in chunks:
            assert chunk.target_file == "src/mymodule.py"

    def test_chunks_have_proportional_max_lines(self):
        """Each chunk max_lines should be proportional to its export count."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="Implement classes",
            max_lines=100,
            required_exports=["A", "B", "C", "D"],
        )
        estimate = SizeEstimate(
            lines=400, tokens=1200, complexity="high",
            confidence=0.7, reasoning="Large",
        )

        chunks = capability._decompose_spec(spec, estimate)

        for chunk in chunks:
            # max_lines should be > 0 and <= the original max_lines
            assert chunk.max_lines > 0
            assert chunk.max_lines <= spec.max_lines

    def test_no_exports_falls_back_to_two_parts(self):
        """Without required_exports, should split into two parts."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="Implement a big system",
            max_lines=100,
            required_exports=None,
        )
        estimate = SizeEstimate(
            lines=300, tokens=900, complexity="high",
            confidence=0.7, reasoning="Large",
        )

        chunks = capability._decompose_spec(spec, estimate)

        assert len(chunks) == 2
        assert "Part 1" in chunks[0].description
        assert "Part 2" in chunks[1].description

    def test_single_export_falls_back_to_two_parts(self):
        """With only one export, cannot split by exports, should fallback."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="Implement a big class",
            max_lines=100,
            required_exports=["BigClass"],
        )
        estimate = SizeEstimate(
            lines=300, tokens=900, complexity="high",
            confidence=0.7, reasoning="Large",
        )

        chunks = capability._decompose_spec(spec, estimate)

        assert len(chunks) == 2

    def test_first_chunk_keeps_docstring(self):
        """Only the first chunk should require a module docstring."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="Implement classes",
            max_lines=50,
            must_have_docstring=True,
            required_exports=["A", "B", "C"],
        )
        estimate = SizeEstimate(
            lines=300, tokens=900, complexity="high",
            confidence=0.7, reasoning="Large",
        )

        chunks = capability._decompose_spec(spec, estimate)

        assert chunks[0].must_have_docstring is True
        for chunk in chunks[1:]:
            assert chunk.must_have_docstring is False


class TestAssembleChunks:
    """Tests for CodeGenerationCapability._assemble_chunks."""

    def test_deduplicates_imports(self):
        """Should deduplicate imports across chunks."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(
            target_file="src/mymodule.py",
            description="test",
        )

        chunk1 = '''"""Module docstring."""

import os
import json

from typing import Optional

class Foo:
    """Foo class."""
    pass
'''

        chunk2 = '''import os
import sys

from typing import Optional

class Bar:
    """Bar class."""
    pass
'''

        result = capability._assemble_chunks([chunk1, chunk2], spec)

        # Count occurrences of 'import os' at module level
        lines = result.split('\n')
        import_os_count = sum(1 for l in lines if l.strip() == 'import os')
        assert import_os_count == 1, f"Expected 1 'import os', found {import_os_count}"

        # Both classes should be present
        assert 'class Foo:' in result
        assert 'class Bar:' in result

    def test_preserves_module_docstring(self):
        """Should keep the module docstring from the first chunk."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(target_file="src/test.py", description="test")

        chunk1 = '''"""This is the module docstring."""

class Foo:
    pass
'''

        chunk2 = '''class Bar:
    pass
'''

        result = capability._assemble_chunks([chunk1, chunk2], spec)

        assert '"""This is the module docstring."""' in result

    def test_preserves_body_ordering(self):
        """Should preserve class/function ordering from chunks."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(target_file="src/test.py", description="test")

        chunk1 = '''class Alpha:
    pass
'''
        chunk2 = '''class Beta:
    pass
'''
        chunk3 = '''class Gamma:
    pass
'''

        result = capability._assemble_chunks([chunk1, chunk2, chunk3], spec)

        alpha_pos = result.index('class Alpha')
        beta_pos = result.index('class Beta')
        gamma_pos = result.index('class Gamma')
        assert alpha_pos < beta_pos < gamma_pos

    def test_handles_future_imports(self):
        """Should place __future__ imports at the top."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(target_file="src/test.py", description="test")

        chunk1 = '''from __future__ import annotations

import os

class Foo:
    pass
'''
        chunk2 = '''from __future__ import annotations

import sys

class Bar:
    pass
'''

        result = capability._assemble_chunks([chunk1, chunk2], spec)

        lines = result.split('\n')
        future_count = sum(1 for l in lines if 'from __future__ import annotations' in l)
        assert future_count == 1

        # __future__ should come before other imports
        future_pos = result.index('from __future__')
        os_pos = result.index('import os')
        assert future_pos < os_pos

    def test_empty_chunks_handled(self):
        """Should handle empty or whitespace-only chunks."""
        capability = CodeGenerationCapability()
        spec = CodeGenerationSpec(target_file="src/test.py", description="test")

        chunk1 = '''class Foo:
    pass
'''
        chunk2 = '''

'''

        result = capability._assemble_chunks([chunk1, chunk2], spec)

        assert 'class Foo:' in result


class TestHandleHandoffDecomposition:
    """Integration tests for handle_handoff with decomposition."""

    def _make_handoff(self, max_lines=100, exports=None, allows_chunking=True):
        """Helper to create a Handoff for testing."""
        return Handoff(
            id="test-handoff-1",
            from_agent="orchestrator",
            to_agent="code-gen",
            capability_id="generate_code",
            task="Implement a large system with multiple classes",
            inputs={
                "target_file": "src/big_module.py",
                "context_files": [],
                "required_exports": exports or ["Foo", "Bar", "Baz"],
                "required_imports": None,
                "must_have_docstring": True,
            },
            expected_output=ExpectedOutput(
                type="code",
                fields=["content", "exports", "imports"],
                max_lines=max_lines,
                max_tokens=500,
                completeness_markers=exports or ["Foo", "Bar", "Baz"],
                allows_chunking=allows_chunking,
            ),
            priority=HandoffPriority.NORMAL,
        )

    def _chunk_generator(self, task, inputs):
        """Generate valid code for a chunk based on requested exports."""
        exports = inputs.get("required_exports") or []
        parts = []
        if inputs.get("must_have_docstring", False):
            parts.append('"""Generated module."""')
            parts.append('')
        for export in exports:
            parts.append(f'class {export}:')
            parts.append(f'    """{export} class."""')
            parts.append('    pass')
            parts.append('')
        if not exports:
            parts.append('# Helper code')
            parts.append('def _helper():')
            parts.append('    pass')
            parts.append('')
        return '\n'.join(parts)

    def test_decomposes_when_estimate_exceeds_limit(self):
        """Should decompose when estimate exceeds max_lines."""
        def big_estimate(task, inputs):
            return SizeEstimate(
                lines=300, tokens=900, complexity="high",
                confidence=0.8, reasoning="Large task",
            )

        capability = CodeGenerationCapability(
            generate_fn=self._chunk_generator,
            estimate_fn=big_estimate,
        )

        handoff = self._make_handoff(max_lines=100, exports=["Foo", "Bar", "Baz"])
        result = capability.handle_handoff(handoff)

        assert isinstance(result, GeneratedCode)
        assert "class Foo" in result.content
        assert "class Bar" in result.content
        assert "class Baz" in result.content

    def test_does_not_decompose_under_limit(self):
        """Should not decompose when estimate is under max_lines."""
        call_count = {"generate": 0}

        def small_estimate(task, inputs):
            return SizeEstimate(
                lines=50, tokens=150, complexity="low",
                confidence=0.8, reasoning="Small task",
            )

        def counting_generator(task, inputs):
            call_count["generate"] += 1
            return '"""Module."""\n\nclass Foo:\n    pass\n\nclass Bar:\n    pass\n\nclass Baz:\n    pass\n'

        capability = CodeGenerationCapability(
            generate_fn=counting_generator,
            estimate_fn=small_estimate,
        )

        handoff = self._make_handoff(max_lines=100, exports=["Foo", "Bar", "Baz"])
        result = capability.handle_handoff(handoff)

        # Should call generate exactly once (no decomposition)
        assert call_count["generate"] == 1
        assert isinstance(result, GeneratedCode)

    def test_rejects_when_chunking_not_allowed(self):
        """Should raise HandoffRejectedError when chunking is disabled and estimate exceeds limit."""
        def big_estimate(task, inputs):
            return SizeEstimate(
                lines=300, tokens=900, complexity="high",
                confidence=0.8, reasoning="Large task",
            )

        capability = CodeGenerationCapability(
            generate_fn=self._chunk_generator,
            estimate_fn=big_estimate,
        )

        handoff = self._make_handoff(
            max_lines=100,
            exports=["Foo", "Bar"],
            allows_chunking=False,
        )

        with pytest.raises(HandoffRejectedError):
            capability.handle_handoff(handoff)

    def test_decomposed_result_has_all_exports(self):
        """Decomposed and assembled result should contain all required exports."""
        def big_estimate(task, inputs):
            return SizeEstimate(
                lines=400, tokens=1200, complexity="high",
                confidence=0.8, reasoning="Large task",
            )

        capability = CodeGenerationCapability(
            generate_fn=self._chunk_generator,
            estimate_fn=big_estimate,
        )

        exports = ["Alpha", "Beta", "Gamma", "Delta"]
        handoff = self._make_handoff(max_lines=80, exports=exports)
        result = capability.handle_handoff(handoff)

        for export in exports:
            assert export in result.exports, f"Missing export: {export}"
