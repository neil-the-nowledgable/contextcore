"""OTel Messaging semantic conventions for alert/webhook processing.

Opt-in feature that adds OTel messaging attributes to alert processing
spans in Rabbit/Fox. Disabled by default.

Enable via:
  CONTEXTCORE_MESSAGING_EMIT=true
  OTEL_SEMCONV_STABILITY_OPT_IN=messaging

See: https://opentelemetry.io/docs/specs/semconv/messaging/
"""

import os
from typing import Any, Dict, Optional

# OTel Messaging semantic convention attribute names
MESSAGING_SYSTEM = "messaging.system"
MESSAGING_DESTINATION_NAME = "messaging.destination.name"
MESSAGING_OPERATION_TYPE = "messaging.operation.type"
MESSAGING_MESSAGE_ID = "messaging.message.id"
MESSAGING_MESSAGE_BODY_SIZE = "messaging.message.body.size"

# Mapping from Rabbit alert.* attributes to OTel messaging conventions
ALERT_TO_MESSAGING_MAPPINGS: Dict[str, str] = {
    "alert.source": MESSAGING_SYSTEM,
    "alert.name": MESSAGING_DESTINATION_NAME,
    "alert.id": MESSAGING_MESSAGE_ID,
}

_cached_enabled: bool | None = None


def get_messaging_emit_enabled() -> bool:
    """Check whether messaging convention emit is enabled.

    Resolution order:
    1. CONTEXTCORE_MESSAGING_EMIT env var (explicit, project-specific)
    2. OTEL_SEMCONV_STABILITY_OPT_IN contains "messaging" token
    3. Default: False (disabled)

    Emits an OTel feature flag evaluation event on first resolution.
    """
    from contextcore.compat.otel_feature_flags import emit_feature_flag_event

    global _cached_enabled
    if _cached_enabled is not None:
        return _cached_enabled

    # 1. ContextCore-specific env var takes precedence
    cc_msg = os.getenv("CONTEXTCORE_MESSAGING_EMIT", "").strip().lower()
    if cc_msg:
        _cached_enabled = cc_msg in ("true", "1", "yes")
        emit_feature_flag_event(
            "contextcore.messaging_emit",
            str(_cached_enabled).lower(),
            "contextcore-env",
        )
        return _cached_enabled

    # 2. OTel standard env var (comma-separated token list)
    otel_opt_in = os.getenv("OTEL_SEMCONV_STABILITY_OPT_IN", "").strip().lower()
    if otel_opt_in:
        tokens = {t.strip() for t in otel_opt_in.split(",")}
        if "messaging" in tokens:
            _cached_enabled = True
            emit_feature_flag_event(
                "contextcore.messaging_emit", "true", "otel-env",
            )
            return _cached_enabled

    # 3. Default: disabled
    _cached_enabled = False
    emit_feature_flag_event(
        "contextcore.messaging_emit", "false", "contextcore-default",
    )
    return _cached_enabled


def build_messaging_attributes(
    system: str,
    destination: str,
    operation: str,
    message_id: Optional[str] = None,
    body_size: Optional[int] = None,
) -> Dict[str, Any]:
    """Build OTel messaging attributes dict.

    Returns an empty dict when messaging emit is disabled.

    Args:
        system: The messaging system (e.g. "grafana", "alertmanager", "manual").
        destination: The destination name (e.g. alert name or webhook path).
        operation: The operation type (e.g. "receive", "process").
        message_id: Optional message/alert identifier.
        body_size: Optional payload size in bytes.
    """
    if not get_messaging_emit_enabled():
        return {}

    attrs: Dict[str, Any] = {
        MESSAGING_SYSTEM: system,
        MESSAGING_DESTINATION_NAME: destination,
        MESSAGING_OPERATION_TYPE: operation,
    }
    if message_id is not None:
        attrs[MESSAGING_MESSAGE_ID] = message_id
    if body_size is not None:
        attrs[MESSAGING_MESSAGE_BODY_SIZE] = body_size
    return attrs


def apply_messaging_attributes(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Add messaging attributes by mapping from existing alert.* keys.

    When enabled, copies the dict and adds messaging.* keys for any
    matching alert.* source keys. When disabled, returns input as-is.
    """
    if not get_messaging_emit_enabled():
        return attributes

    result = dict(attributes)
    for source_key, messaging_key in ALERT_TO_MESSAGING_MAPPINGS.items():
        if source_key in result:
            result[messaging_key] = result[source_key]
    return result


def reset_cache() -> None:
    """Reset the cached enabled state. For test isolation."""
    global _cached_enabled
    _cached_enabled = None
