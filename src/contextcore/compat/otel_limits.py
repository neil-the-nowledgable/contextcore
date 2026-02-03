"""OTel attribute limits configuration for long-running task spans.

Configures SpanLimits to prevent oversized spans from tasks that accumulate
many status change events over time. Reads ContextCore-specific overrides
and falls back to OTel SDK defaults.

OTel SDK environment variables (and their defaults):
  OTEL_ATTRIBUTE_COUNT_LIMIT          (default 128)
  OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT   (default unlimited)
  OTEL_SPAN_EVENT_COUNT_LIMIT         (default 128)
  OTEL_SPAN_LINK_COUNT_LIMIT          (default 128)
  OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT     (inherits OTEL_ATTRIBUTE_COUNT_LIMIT)

ContextCore-specific overrides:
  CONTEXTCORE_SPAN_EVENT_LIMIT        overrides OTEL_SPAN_EVENT_COUNT_LIMIT
  CONTEXTCORE_SPAN_LINK_LIMIT         overrides OTEL_SPAN_LINK_COUNT_LIMIT

Enable via:
  CONTEXTCORE_SPAN_EVENT_LIMIT=256
  CONTEXTCORE_SPAN_LINK_LIMIT=64
"""

import os
from typing import Optional

from opentelemetry.sdk.trace import SpanLimits

# ContextCore-specific env var names
CONTEXTCORE_SPAN_EVENT_LIMIT_ENV = "CONTEXTCORE_SPAN_EVENT_LIMIT"
CONTEXTCORE_SPAN_LINK_LIMIT_ENV = "CONTEXTCORE_SPAN_LINK_LIMIT"

# OTel standard env var names (for reference)
OTEL_SPAN_EVENT_COUNT_LIMIT_ENV = "OTEL_SPAN_EVENT_COUNT_LIMIT"
OTEL_SPAN_LINK_COUNT_LIMIT_ENV = "OTEL_SPAN_LINK_COUNT_LIMIT"

_cached_limits: Optional[SpanLimits] = None


def _parse_int_env(name: str) -> Optional[int]:
    """Parse an integer from an environment variable, returning None if unset or invalid."""
    val = os.getenv(name, "").strip()
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


def get_span_limits() -> SpanLimits:
    """Build a SpanLimits object from environment variables.

    Resolution order for each limit:
    1. ContextCore-specific env var (e.g. CONTEXTCORE_SPAN_EVENT_LIMIT)
    2. OTel standard env var (read automatically by SpanLimits constructor)
    3. OTel SDK default

    Emits an OTel feature flag evaluation event when ContextCore-specific
    overrides are active.

    Returns:
        SpanLimits configured from environment variables.
    """
    from contextcore.compat.otel_feature_flags import emit_feature_flag_event

    global _cached_limits
    if _cached_limits is not None:
        return _cached_limits

    kwargs = {}
    cc_overrides_active = False

    # Check ContextCore-specific event limit
    cc_event_limit = _parse_int_env(CONTEXTCORE_SPAN_EVENT_LIMIT_ENV)
    if cc_event_limit is not None:
        kwargs["max_events"] = cc_event_limit
        cc_overrides_active = True

    # Check ContextCore-specific link limit
    cc_link_limit = _parse_int_env(CONTEXTCORE_SPAN_LINK_LIMIT_ENV)
    if cc_link_limit is not None:
        kwargs["max_links"] = cc_link_limit
        cc_overrides_active = True

    # Build SpanLimits. When kwargs are empty the constructor reads
    # standard OTEL_* env vars and applies OTel defaults automatically.
    _cached_limits = SpanLimits(**kwargs)

    # Emit feature flag event for audit trail
    if cc_overrides_active:
        parts = []
        if cc_event_limit is not None:
            parts.append(f"events={cc_event_limit}")
        if cc_link_limit is not None:
            parts.append(f"links={cc_link_limit}")
        emit_feature_flag_event(
            "contextcore.span_limits",
            ",".join(parts),
            "contextcore-env",
        )
    else:
        emit_feature_flag_event(
            "contextcore.span_limits",
            "default",
            "contextcore-default",
        )

    return _cached_limits


def configure_span_limits() -> SpanLimits:
    """Configure and return SpanLimits for ContextCore TracerProviders.

    Convenience alias for get_span_limits(). Use this when initializing
    a TracerProvider:

        from contextcore.compat.otel_limits import configure_span_limits
        provider = TracerProvider(span_limits=configure_span_limits())

    Returns:
        SpanLimits configured from environment variables.
    """
    return get_span_limits()


def reset_cache() -> None:
    """Reset the cached SpanLimits. For test isolation."""
    global _cached_limits
    _cached_limits = None
