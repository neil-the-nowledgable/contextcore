"""Tests for OTel CI/CD semantic conventions dual-emit layer."""

import os
import unittest
from unittest.mock import patch

from contextcore.compat.otel_cicd import (
    CICD_ATTRIBUTE_MAPPINGS,
    apply_cicd_attributes,
    get_cicd_emit_enabled,
    reset_cache,
)


class TestGetCicdEmitEnabled(unittest.TestCase):
    """Tests for get_cicd_emit_enabled()."""

    def setUp(self):
        reset_cache()

    def tearDown(self):
        reset_cache()

    @patch.dict(os.environ, {}, clear=True)
    def test_default_disabled(self):
        self.assertFalse(get_cicd_emit_enabled())

    @patch.dict(os.environ, {"CONTEXTCORE_CICD_EMIT": "true"}, clear=True)
    def test_enabled_via_contextcore_env(self):
        self.assertTrue(get_cicd_emit_enabled())

    @patch.dict(os.environ, {"CONTEXTCORE_CICD_EMIT": "1"}, clear=True)
    def test_enabled_via_contextcore_env_numeric(self):
        self.assertTrue(get_cicd_emit_enabled())

    @patch.dict(os.environ, {"CONTEXTCORE_CICD_EMIT": "yes"}, clear=True)
    def test_enabled_via_contextcore_env_yes(self):
        self.assertTrue(get_cicd_emit_enabled())

    @patch.dict(os.environ, {"CONTEXTCORE_CICD_EMIT": "false"}, clear=True)
    def test_disabled_via_contextcore_env(self):
        self.assertFalse(get_cicd_emit_enabled())

    @patch.dict(
        os.environ,
        {"OTEL_SEMCONV_STABILITY_OPT_IN": "cicd"},
        clear=True,
    )
    def test_enabled_via_otel_opt_in(self):
        self.assertTrue(get_cicd_emit_enabled())

    @patch.dict(
        os.environ,
        {"OTEL_SEMCONV_STABILITY_OPT_IN": "gen_ai_latest_experimental,cicd"},
        clear=True,
    )
    def test_enabled_via_otel_opt_in_multiple_tokens(self):
        self.assertTrue(get_cicd_emit_enabled())

    @patch.dict(
        os.environ,
        {"OTEL_SEMCONV_STABILITY_OPT_IN": "gen_ai_latest_experimental"},
        clear=True,
    )
    def test_otel_opt_in_without_cicd_token(self):
        self.assertFalse(get_cicd_emit_enabled())

    @patch.dict(
        os.environ,
        {
            "CONTEXTCORE_CICD_EMIT": "false",
            "OTEL_SEMCONV_STABILITY_OPT_IN": "cicd",
        },
        clear=True,
    )
    def test_contextcore_env_overrides_otel(self):
        self.assertFalse(get_cicd_emit_enabled())

    @patch.dict(os.environ, {"CONTEXTCORE_CICD_EMIT": "true"}, clear=True)
    def test_caching_behavior(self):
        self.assertTrue(get_cicd_emit_enabled())
        # Changing env after first call should not change result (cached)
        os.environ["CONTEXTCORE_CICD_EMIT"] = "false"
        self.assertTrue(get_cicd_emit_enabled())
        # Reset cache and re-check
        reset_cache()
        self.assertFalse(get_cicd_emit_enabled())


class TestApplyCicdAttributes(unittest.TestCase):
    """Tests for apply_cicd_attributes()."""

    def setUp(self):
        reset_cache()

    def tearDown(self):
        reset_cache()

    @patch.dict(os.environ, {}, clear=True)
    def test_disabled_returns_same_object(self):
        attrs = {"task.id": "T-1", "task.title": "Test"}
        result = apply_cicd_attributes(attrs)
        self.assertIs(result, attrs)
        self.assertNotIn("cicd.pipeline.task.run.id", result)

    @patch.dict(os.environ, {"CONTEXTCORE_CICD_EMIT": "true"}, clear=True)
    def test_enabled_adds_all_cicd_attributes(self):
        attrs = {
            "project.name": "my-project",
            "sprint.id": "sprint-3",
            "task.title": "Implement feature",
            "task.id": "PROJ-123",
            "task.type": "story",
        }
        result = apply_cicd_attributes(attrs)
        self.assertEqual(result["cicd.pipeline.name"], "my-project")
        self.assertEqual(result["cicd.pipeline.run.id"], "sprint-3")
        self.assertEqual(result["cicd.pipeline.task.name"], "Implement feature")
        self.assertEqual(result["cicd.pipeline.task.run.id"], "PROJ-123")
        self.assertEqual(result["cicd.pipeline.task.type"], "story")
        # Originals preserved
        self.assertEqual(result["task.id"], "PROJ-123")
        self.assertEqual(result["project.name"], "my-project")

    @patch.dict(os.environ, {"CONTEXTCORE_CICD_EMIT": "true"}, clear=True)
    def test_partial_input_maps_only_present_keys(self):
        attrs = {"task.id": "T-1", "other.attr": "value"}
        result = apply_cicd_attributes(attrs)
        self.assertEqual(result["cicd.pipeline.task.run.id"], "T-1")
        self.assertNotIn("cicd.pipeline.name", result)
        self.assertNotIn("cicd.pipeline.run.id", result)
        self.assertNotIn("cicd.pipeline.task.name", result)
        self.assertNotIn("cicd.pipeline.task.type", result)
        self.assertEqual(result["other.attr"], "value")

    @patch.dict(os.environ, {"CONTEXTCORE_CICD_EMIT": "true"}, clear=True)
    def test_does_not_mutate_input(self):
        attrs = {"task.id": "T-1", "task.title": "Test"}
        original = dict(attrs)
        result = apply_cicd_attributes(attrs)
        self.assertEqual(attrs, original)
        self.assertIsNot(result, attrs)


if __name__ == "__main__":
    unittest.main()
