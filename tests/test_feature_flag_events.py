"""Tests for OTel feature flag evaluation events."""

import logging
import os
import unittest
from unittest.mock import MagicMock, patch

from opentelemetry import trace

from contextcore.compat.otel_feature_flags import (
    FEATURE_FLAG_KEY,
    FEATURE_FLAG_PROVIDER_NAME,
    FEATURE_FLAG_VALUE,
    FEATURE_FLAG_VARIANT,
    emit_feature_flag_event,
)


class TestEmitFeatureFlagEvent(unittest.TestCase):
    """Tests for emit_feature_flag_event()."""

    def test_adds_event_to_recording_span(self):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        with patch.object(trace, "get_current_span", return_value=mock_span):
            emit_feature_flag_event("contextcore.emit_mode", "dual", "contextcore-default")

        mock_span.add_event.assert_called_once()
        call_args = mock_span.add_event.call_args
        self.assertEqual(call_args[0][0], "feature_flag")
        attrs = call_args[1]["attributes"]
        self.assertEqual(attrs[FEATURE_FLAG_KEY], "contextcore.emit_mode")
        self.assertEqual(attrs[FEATURE_FLAG_VARIANT], "dual")
        self.assertEqual(attrs[FEATURE_FLAG_PROVIDER_NAME], "contextcore-default")
        self.assertNotIn(FEATURE_FLAG_VALUE, attrs)

    def test_includes_value_when_provided(self):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        with patch.object(trace, "get_current_span", return_value=mock_span):
            emit_feature_flag_event("contextcore.cicd_emit", "true", "contextcore-env", value=True)

        attrs = mock_span.add_event.call_args[1]["attributes"]
        self.assertEqual(attrs[FEATURE_FLAG_VALUE], "True")

    def test_skips_span_event_when_not_recording(self):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = False
        with patch.object(trace, "get_current_span", return_value=mock_span):
            emit_feature_flag_event("contextcore.emit_mode", "otel", "otel-env")

        mock_span.add_event.assert_not_called()

    def test_emits_log_regardless_of_span(self):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = False
        with patch.object(trace, "get_current_span", return_value=mock_span), \
             patch("contextcore.compat.otel_feature_flags.logger") as mock_logger:
            emit_feature_flag_event("contextcore.emit_mode", "legacy", "contextcore-env")

        mock_logger.info.assert_called_once()
        log_args = mock_logger.info.call_args
        self.assertIn("contextcore.emit_mode", log_args[0][1])
        self.assertIn("legacy", log_args[0][2])


class TestEmitModeFeatureFlag(unittest.TestCase):
    """Tests that get_emit_mode() emits feature flag events."""

    def setUp(self):
        # Reset otel_genai cache
        import contextcore.compat.otel_genai as genai_mod
        self._genai_mod = genai_mod
        self._original = genai_mod._cached_mode
        genai_mod._cached_mode = None

    def tearDown(self):
        self._genai_mod._cached_mode = self._original

    @patch("contextcore.compat.otel_feature_flags.trace")
    @patch.dict(os.environ, {"CONTEXTCORE_EMIT_MODE": "otel"}, clear=True)
    def test_emit_mode_fires_flag_event_contextcore_env(self, mock_trace):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_trace.get_current_span.return_value = mock_span

        from contextcore.compat.otel_genai import get_emit_mode
        mode = get_emit_mode()

        self.assertEqual(mode.value, "otel")
        mock_span.add_event.assert_called_once()
        attrs = mock_span.add_event.call_args[1]["attributes"]
        self.assertEqual(attrs[FEATURE_FLAG_KEY], "contextcore.emit_mode")
        self.assertEqual(attrs[FEATURE_FLAG_VARIANT], "otel")
        self.assertEqual(attrs[FEATURE_FLAG_PROVIDER_NAME], "contextcore-env")

    @patch("contextcore.compat.otel_feature_flags.trace")
    @patch.dict(
        os.environ,
        {"OTEL_SEMCONV_STABILITY_OPT_IN": "gen_ai_latest_experimental"},
        clear=True,
    )
    def test_emit_mode_fires_flag_event_otel_env(self, mock_trace):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_trace.get_current_span.return_value = mock_span

        from contextcore.compat.otel_genai import get_emit_mode
        mode = get_emit_mode()

        self.assertEqual(mode.value, "otel")
        attrs = mock_span.add_event.call_args[1]["attributes"]
        self.assertEqual(attrs[FEATURE_FLAG_PROVIDER_NAME], "otel-env")

    @patch("contextcore.compat.otel_feature_flags.trace")
    @patch.dict(os.environ, {}, clear=True)
    def test_emit_mode_fires_flag_event_default(self, mock_trace):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_trace.get_current_span.return_value = mock_span

        from contextcore.compat.otel_genai import get_emit_mode
        mode = get_emit_mode()

        self.assertEqual(mode.value, "dual")
        attrs = mock_span.add_event.call_args[1]["attributes"]
        self.assertEqual(attrs[FEATURE_FLAG_VARIANT], "dual")
        self.assertEqual(attrs[FEATURE_FLAG_PROVIDER_NAME], "contextcore-default")

    @patch("contextcore.compat.otel_feature_flags.trace")
    @patch.dict(os.environ, {"CONTEXTCORE_EMIT_MODE": "dual"}, clear=True)
    def test_cached_call_does_not_re_emit(self, mock_trace):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_trace.get_current_span.return_value = mock_span

        from contextcore.compat.otel_genai import get_emit_mode
        get_emit_mode()
        get_emit_mode()  # second call should be cached

        self.assertEqual(mock_span.add_event.call_count, 1)


class TestCicdEmitFeatureFlag(unittest.TestCase):
    """Tests that get_cicd_emit_enabled() emits feature flag events."""

    def setUp(self):
        from contextcore.compat.otel_cicd import reset_cache
        reset_cache()

    def tearDown(self):
        from contextcore.compat.otel_cicd import reset_cache
        reset_cache()

    @patch("contextcore.compat.otel_feature_flags.trace")
    @patch.dict(os.environ, {"CONTEXTCORE_CICD_EMIT": "true"}, clear=True)
    def test_cicd_emit_fires_flag_event_enabled(self, mock_trace):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_trace.get_current_span.return_value = mock_span

        from contextcore.compat.otel_cicd import get_cicd_emit_enabled
        result = get_cicd_emit_enabled()

        self.assertTrue(result)
        mock_span.add_event.assert_called_once()
        attrs = mock_span.add_event.call_args[1]["attributes"]
        self.assertEqual(attrs[FEATURE_FLAG_KEY], "contextcore.cicd_emit")
        self.assertEqual(attrs[FEATURE_FLAG_VARIANT], "true")
        self.assertEqual(attrs[FEATURE_FLAG_PROVIDER_NAME], "contextcore-env")

    @patch("contextcore.compat.otel_feature_flags.trace")
    @patch.dict(os.environ, {}, clear=True)
    def test_cicd_emit_fires_flag_event_default(self, mock_trace):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_trace.get_current_span.return_value = mock_span

        from contextcore.compat.otel_cicd import get_cicd_emit_enabled
        result = get_cicd_emit_enabled()

        self.assertFalse(result)
        attrs = mock_span.add_event.call_args[1]["attributes"]
        self.assertEqual(attrs[FEATURE_FLAG_VARIANT], "false")
        self.assertEqual(attrs[FEATURE_FLAG_PROVIDER_NAME], "contextcore-default")

    @patch("contextcore.compat.otel_feature_flags.trace")
    @patch.dict(
        os.environ,
        {"OTEL_SEMCONV_STABILITY_OPT_IN": "cicd"},
        clear=True,
    )
    def test_cicd_emit_fires_flag_event_otel_env(self, mock_trace):
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_trace.get_current_span.return_value = mock_span

        from contextcore.compat.otel_cicd import get_cicd_emit_enabled
        result = get_cicd_emit_enabled()

        self.assertTrue(result)
        attrs = mock_span.add_event.call_args[1]["attributes"]
        self.assertEqual(attrs[FEATURE_FLAG_PROVIDER_NAME], "otel-env")


if __name__ == "__main__":
    unittest.main()
