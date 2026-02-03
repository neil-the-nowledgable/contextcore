"""
Tests for OTel span limits configuration.

Verifies that get_span_limits() correctly reads ContextCore-specific and
standard OTel env vars to build a SpanLimits object.
"""

import os

import pytest
from unittest.mock import patch

from opentelemetry.sdk.trace import SpanLimits

from contextcore.compat.otel_limits import (
    get_span_limits,
    configure_span_limits,
    reset_cache,
    CONTEXTCORE_SPAN_EVENT_LIMIT_ENV,
    CONTEXTCORE_SPAN_LINK_LIMIT_ENV,
)
from contextcore.contracts import SpanLimitConfig


@pytest.fixture(autouse=True)
def clear_cache():
    """Reset the cached SpanLimits before and after each test."""
    reset_cache()
    yield
    reset_cache()


@pytest.fixture
def clean_env():
    """Remove all span-limit env vars for a clean test environment."""
    env_vars = [
        "CONTEXTCORE_SPAN_EVENT_LIMIT",
        "CONTEXTCORE_SPAN_LINK_LIMIT",
        "OTEL_SPAN_EVENT_COUNT_LIMIT",
        "OTEL_SPAN_LINK_COUNT_LIMIT",
        "OTEL_ATTRIBUTE_COUNT_LIMIT",
        "OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT",
        "OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT",
    ]
    saved = {}
    for var in env_vars:
        if var in os.environ:
            saved[var] = os.environ.pop(var)
    yield
    # Restore any env vars that were present
    for var in env_vars:
        if var in saved:
            os.environ[var] = saved[var]
        elif var in os.environ:
            del os.environ[var]


class TestGetSpanLimitsDefaults:
    """Test that defaults are returned when no env vars are set."""

    def test_returns_span_limits_instance(self, clean_env):
        limits = get_span_limits()
        assert isinstance(limits, SpanLimits)

    def test_default_max_events(self, clean_env):
        limits = get_span_limits()
        assert limits.max_events == 128

    def test_default_max_links(self, clean_env):
        limits = get_span_limits()
        assert limits.max_links == 128

    def test_default_max_attributes(self, clean_env):
        limits = get_span_limits()
        assert limits.max_attributes == 128


class TestContextCoreOverrides:
    """Test ContextCore-specific env var overrides."""

    def test_event_limit_override(self, clean_env):
        os.environ["CONTEXTCORE_SPAN_EVENT_LIMIT"] = "256"
        limits = get_span_limits()
        assert limits.max_events == 256

    def test_link_limit_override(self, clean_env):
        os.environ["CONTEXTCORE_SPAN_LINK_LIMIT"] = "64"
        limits = get_span_limits()
        assert limits.max_links == 64

    def test_both_overrides(self, clean_env):
        os.environ["CONTEXTCORE_SPAN_EVENT_LIMIT"] = "512"
        os.environ["CONTEXTCORE_SPAN_LINK_LIMIT"] = "32"
        limits = get_span_limits()
        assert limits.max_events == 512
        assert limits.max_links == 32

    def test_invalid_value_ignored(self, clean_env):
        os.environ["CONTEXTCORE_SPAN_EVENT_LIMIT"] = "not_a_number"
        limits = get_span_limits()
        # Falls through to OTel defaults
        assert limits.max_events == 128

    def test_empty_value_ignored(self, clean_env):
        os.environ["CONTEXTCORE_SPAN_EVENT_LIMIT"] = ""
        limits = get_span_limits()
        assert limits.max_events == 128


class TestOtelStandardEnvVars:
    """Test that OTel standard env vars are respected."""

    def test_otel_event_count_limit(self, clean_env):
        os.environ["OTEL_SPAN_EVENT_COUNT_LIMIT"] = "64"
        limits = get_span_limits()
        assert limits.max_events == 64

    def test_otel_link_count_limit(self, clean_env):
        os.environ["OTEL_SPAN_LINK_COUNT_LIMIT"] = "32"
        limits = get_span_limits()
        assert limits.max_links == 32

    def test_contextcore_takes_precedence_over_otel(self, clean_env):
        os.environ["OTEL_SPAN_EVENT_COUNT_LIMIT"] = "64"
        os.environ["CONTEXTCORE_SPAN_EVENT_LIMIT"] = "512"
        limits = get_span_limits()
        assert limits.max_events == 512


class TestCaching:
    """Test that results are cached correctly."""

    def test_returns_same_object(self, clean_env):
        limits1 = get_span_limits()
        limits2 = get_span_limits()
        assert limits1 is limits2

    def test_reset_cache_clears(self, clean_env):
        limits1 = get_span_limits()
        reset_cache()
        limits2 = get_span_limits()
        assert limits1 is not limits2

    def test_cache_ignores_env_changes(self, clean_env):
        limits1 = get_span_limits()
        os.environ["CONTEXTCORE_SPAN_EVENT_LIMIT"] = "999"
        limits2 = get_span_limits()
        # Still returns cached value
        assert limits2.max_events == limits1.max_events


class TestConfigureSpanLimits:
    """Test the convenience alias."""

    def test_configure_returns_same_as_get(self, clean_env):
        limits = configure_span_limits()
        assert isinstance(limits, SpanLimits)
        assert limits is get_span_limits()


class TestSpanLimitConfigContract:
    """Test that contract enum values match actual env var names."""

    def test_event_limit_env_name(self):
        assert SpanLimitConfig.SPAN_EVENT_LIMIT.value == "CONTEXTCORE_SPAN_EVENT_LIMIT"
        assert SpanLimitConfig.SPAN_EVENT_LIMIT.value == CONTEXTCORE_SPAN_EVENT_LIMIT_ENV

    def test_link_limit_env_name(self):
        assert SpanLimitConfig.SPAN_LINK_LIMIT.value == "CONTEXTCORE_SPAN_LINK_LIMIT"
        assert SpanLimitConfig.SPAN_LINK_LIMIT.value == CONTEXTCORE_SPAN_LINK_LIMIT_ENV


class TestFeatureFlagEvent:
    """Test that feature flag events are emitted correctly."""

    def test_default_emits_default_variant(self, clean_env):
        with patch("contextcore.compat.otel_feature_flags.emit_feature_flag_event") as mock:
            from contextcore.compat import otel_limits
            otel_limits.reset_cache()
            otel_limits.get_span_limits()
            mock.assert_called_once_with(
                "contextcore.span_limits",
                "default",
                "contextcore-default",
            )

    def test_override_emits_contextcore_env_variant(self, clean_env):
        os.environ["CONTEXTCORE_SPAN_EVENT_LIMIT"] = "256"
        with patch("contextcore.compat.otel_feature_flags.emit_feature_flag_event") as mock:
            from contextcore.compat import otel_limits
            otel_limits.reset_cache()
            otel_limits.get_span_limits()
            mock.assert_called_once_with(
                "contextcore.span_limits",
                "events=256",
                "contextcore-env",
            )

    def test_both_overrides_emit_combined_variant(self, clean_env):
        os.environ["CONTEXTCORE_SPAN_EVENT_LIMIT"] = "256"
        os.environ["CONTEXTCORE_SPAN_LINK_LIMIT"] = "64"
        with patch("contextcore.compat.otel_feature_flags.emit_feature_flag_event") as mock:
            from contextcore.compat import otel_limits
            otel_limits.reset_cache()
            otel_limits.get_span_limits()
            mock.assert_called_once_with(
                "contextcore.span_limits",
                "events=256,links=64",
                "contextcore-env",
            )
