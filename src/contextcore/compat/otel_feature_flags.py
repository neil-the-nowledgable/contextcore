"""OTel Feature Flag semantic conventions for ContextCore configuration flags.

Emits feature_flag evaluation events on the current span (if active) and
via Python logging (for Loki ingestion) whenever a ContextCore configuration
flag is first resolved.

See: https://opentelemetry.io/docs/specs/semconv/feature-flags/feature-flags-events/
"""

import logging
from typing import Any, Optional

from opentelemetry import trace

logger = logging.getLogger(__name__)

# OTel Feature Flag semantic convention attribute names
FEATURE_FLAG_KEY = "feature_flag.key"
FEATURE_FLAG_PROVIDER_NAME = "feature_flag.provider_name"
FEATURE_FLAG_VARIANT = "feature_flag.result.variant"
FEATURE_FLAG_VALUE = "feature_flag.result.value"


def emit_feature_flag_event(
    flag_key: str,
    variant: str,
    provider_name: str = "contextcore-env",
    value: Optional[Any] = None,
) -> None:
    """Emit an OTel feature flag evaluation event.

    Adds a ``feature_flag`` event to the current span (if one is recording)
    with standard OTel feature flag attributes.  Also emits a structured log
    so the evaluation is captured in Loki regardless of span availability.

    Args:
        flag_key: The feature flag identifier (e.g. "contextcore.emit_mode").
        variant: The resolved variant string (e.g. "dual", "true").
        provider_name: Source that provided the value. One of
            "contextcore-env", "otel-env", or "contextcore-default".
        value: Optional raw value (stringified in the event).
    """
    attributes: dict[str, str] = {
        FEATURE_FLAG_KEY: flag_key,
        FEATURE_FLAG_PROVIDER_NAME: provider_name,
        FEATURE_FLAG_VARIANT: variant,
    }
    if value is not None:
        attributes[FEATURE_FLAG_VALUE] = str(value)

    # Add event to current span if one is recording
    span = trace.get_current_span()
    if span.is_recording():
        span.add_event("feature_flag", attributes=attributes)

    # Structured log for Loki ingestion
    logger.info(
        "feature_flag.evaluation: %s=%s (provider=%s)",
        flag_key,
        variant,
        provider_name,
        extra={"feature_flag": attributes},
    )
