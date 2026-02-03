"""Tests for OTel Messaging semantic conventions compat layer."""

import os
import unittest
from unittest.mock import patch

from contextcore.compat.otel_messaging import (
    ALERT_TO_MESSAGING_MAPPINGS,
    MESSAGING_DESTINATION_NAME,
    MESSAGING_MESSAGE_BODY_SIZE,
    MESSAGING_MESSAGE_ID,
    MESSAGING_OPERATION_TYPE,
    MESSAGING_SYSTEM,
    apply_messaging_attributes,
    build_messaging_attributes,
    get_messaging_emit_enabled,
    reset_cache,
)


class TestGetMessagingEmitEnabled(unittest.TestCase):
    """Tests for get_messaging_emit_enabled()."""

    def setUp(self):
        reset_cache()

    def tearDown(self):
        reset_cache()

    @patch.dict(os.environ, {}, clear=True)
    def test_default_disabled(self):
        self.assertFalse(get_messaging_emit_enabled())

    @patch.dict(os.environ, {"CONTEXTCORE_MESSAGING_EMIT": "true"}, clear=True)
    def test_enabled_via_contextcore_env(self):
        self.assertTrue(get_messaging_emit_enabled())

    @patch.dict(os.environ, {"CONTEXTCORE_MESSAGING_EMIT": "false"}, clear=True)
    def test_disabled_via_contextcore_env(self):
        self.assertFalse(get_messaging_emit_enabled())

    @patch.dict(
        os.environ,
        {"OTEL_SEMCONV_STABILITY_OPT_IN": "messaging"},
        clear=True,
    )
    def test_enabled_via_otel_opt_in(self):
        self.assertTrue(get_messaging_emit_enabled())

    @patch.dict(
        os.environ,
        {"OTEL_SEMCONV_STABILITY_OPT_IN": "cicd,messaging"},
        clear=True,
    )
    def test_enabled_via_otel_opt_in_multiple_tokens(self):
        self.assertTrue(get_messaging_emit_enabled())

    @patch.dict(
        os.environ,
        {"OTEL_SEMCONV_STABILITY_OPT_IN": "cicd"},
        clear=True,
    )
    def test_otel_opt_in_without_messaging_token(self):
        self.assertFalse(get_messaging_emit_enabled())

    @patch.dict(
        os.environ,
        {
            "CONTEXTCORE_MESSAGING_EMIT": "false",
            "OTEL_SEMCONV_STABILITY_OPT_IN": "messaging",
        },
        clear=True,
    )
    def test_contextcore_env_overrides_otel(self):
        self.assertFalse(get_messaging_emit_enabled())

    @patch.dict(os.environ, {"CONTEXTCORE_MESSAGING_EMIT": "true"}, clear=True)
    def test_caching_behavior(self):
        self.assertTrue(get_messaging_emit_enabled())
        os.environ["CONTEXTCORE_MESSAGING_EMIT"] = "false"
        self.assertTrue(get_messaging_emit_enabled())  # cached
        reset_cache()
        self.assertFalse(get_messaging_emit_enabled())


class TestBuildMessagingAttributes(unittest.TestCase):
    """Tests for build_messaging_attributes()."""

    def setUp(self):
        reset_cache()

    def tearDown(self):
        reset_cache()

    @patch.dict(os.environ, {}, clear=True)
    def test_disabled_returns_empty_dict(self):
        result = build_messaging_attributes("grafana", "alert1", "receive")
        self.assertEqual(result, {})

    @patch.dict(os.environ, {"CONTEXTCORE_MESSAGING_EMIT": "true"}, clear=True)
    def test_enabled_builds_required_attrs(self):
        result = build_messaging_attributes("grafana", "HighErrorRate", "receive")
        self.assertEqual(result[MESSAGING_SYSTEM], "grafana")
        self.assertEqual(result[MESSAGING_DESTINATION_NAME], "HighErrorRate")
        self.assertEqual(result[MESSAGING_OPERATION_TYPE], "receive")
        self.assertNotIn(MESSAGING_MESSAGE_ID, result)
        self.assertNotIn(MESSAGING_MESSAGE_BODY_SIZE, result)

    @patch.dict(os.environ, {"CONTEXTCORE_MESSAGING_EMIT": "true"}, clear=True)
    def test_enabled_includes_optional_attrs(self):
        result = build_messaging_attributes(
            "alertmanager", "alert1", "process",
            message_id="abc-123", body_size=512,
        )
        self.assertEqual(result[MESSAGING_MESSAGE_ID], "abc-123")
        self.assertEqual(result[MESSAGING_MESSAGE_BODY_SIZE], 512)


class TestApplyMessagingAttributes(unittest.TestCase):
    """Tests for apply_messaging_attributes()."""

    def setUp(self):
        reset_cache()

    def tearDown(self):
        reset_cache()

    @patch.dict(os.environ, {}, clear=True)
    def test_disabled_returns_same_object(self):
        attrs = {"alert.source": "grafana", "alert.name": "HighCPU"}
        result = apply_messaging_attributes(attrs)
        self.assertIs(result, attrs)

    @patch.dict(os.environ, {"CONTEXTCORE_MESSAGING_EMIT": "true"}, clear=True)
    def test_enabled_maps_alert_attrs(self):
        attrs = {
            "alert.source": "grafana",
            "alert.name": "HighCPU",
            "alert.id": "fp-123",
        }
        result = apply_messaging_attributes(attrs)
        self.assertEqual(result[MESSAGING_SYSTEM], "grafana")
        self.assertEqual(result[MESSAGING_DESTINATION_NAME], "HighCPU")
        self.assertEqual(result[MESSAGING_MESSAGE_ID], "fp-123")
        # Originals preserved
        self.assertEqual(result["alert.source"], "grafana")
        self.assertEqual(result["alert.name"], "HighCPU")

    @patch.dict(os.environ, {"CONTEXTCORE_MESSAGING_EMIT": "true"}, clear=True)
    def test_partial_input_maps_only_present_keys(self):
        attrs = {"alert.source": "manual", "other": "value"}
        result = apply_messaging_attributes(attrs)
        self.assertEqual(result[MESSAGING_SYSTEM], "manual")
        self.assertNotIn(MESSAGING_DESTINATION_NAME, result)
        self.assertNotIn(MESSAGING_MESSAGE_ID, result)

    @patch.dict(os.environ, {"CONTEXTCORE_MESSAGING_EMIT": "true"}, clear=True)
    def test_does_not_mutate_input(self):
        attrs = {"alert.source": "grafana", "alert.name": "Test"}
        original = dict(attrs)
        apply_messaging_attributes(attrs)
        self.assertEqual(attrs, original)


if __name__ == "__main__":
    unittest.main()
