"""OTel batch processor environment variable documentation and diagnostics.

The OTel Python SDK automatically respects standard environment variables
for tuning BatchSpanProcessor and BatchLogRecordProcessor behavior.
ContextCore uses default BatchSpanProcessor settings, which means these
env vars work out of the box -- no ContextCore-specific configuration needed.

This module documents the env vars, their defaults, and provides helper
functions for surfacing the active configuration in diagnostics and logs.

Span processor env vars:
  OTEL_BSP_SCHEDULE_DELAY       - Delay between batch exports (ms, default 5000)
  OTEL_BSP_MAX_QUEUE_SIZE       - Max spans queued before dropping (default 2048)
  OTEL_BSP_MAX_EXPORT_BATCH_SIZE - Max spans per batch export (default 512)
  OTEL_BSP_EXPORT_TIMEOUT       - Export timeout per batch (ms, default 30000)

Log processor env vars:
  OTEL_BLRP_SCHEDULE_DELAY       - Delay between log batch exports (ms, default 5000)
  OTEL_BLRP_MAX_QUEUE_SIZE       - Max log records queued (default 2048)
  OTEL_BLRP_MAX_EXPORT_BATCH_SIZE - Max log records per batch (default 512)
  OTEL_BLRP_EXPORT_TIMEOUT       - Log export timeout per batch (ms, default 30000)

See: https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/
"""

import logging
import os
from typing import Dict, Union

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# BatchSpanProcessor defaults (OTel SDK standard)
# ---------------------------------------------------------------------------
BSP_SCHEDULE_DELAY_MS = 5000
BSP_MAX_QUEUE_SIZE = 2048
BSP_MAX_EXPORT_BATCH_SIZE = 512
BSP_EXPORT_TIMEOUT_MS = 30000

# ---------------------------------------------------------------------------
# BatchLogRecordProcessor defaults (OTel SDK standard)
# ---------------------------------------------------------------------------
BLRP_SCHEDULE_DELAY_MS = 5000
BLRP_MAX_QUEUE_SIZE = 2048
BLRP_MAX_EXPORT_BATCH_SIZE = 512
BLRP_EXPORT_TIMEOUT_MS = 30000

# Mapping of env var name -> (description, default value)
_BATCH_ENV_VARS: Dict[str, tuple] = {
    # Span processor
    "OTEL_BSP_SCHEDULE_DELAY": ("Span batch export delay (ms)", BSP_SCHEDULE_DELAY_MS),
    "OTEL_BSP_MAX_QUEUE_SIZE": ("Max queued spans", BSP_MAX_QUEUE_SIZE),
    "OTEL_BSP_MAX_EXPORT_BATCH_SIZE": ("Max spans per export batch", BSP_MAX_EXPORT_BATCH_SIZE),
    "OTEL_BSP_EXPORT_TIMEOUT": ("Span export timeout (ms)", BSP_EXPORT_TIMEOUT_MS),
    # Log processor
    "OTEL_BLRP_SCHEDULE_DELAY": ("Log batch export delay (ms)", BLRP_SCHEDULE_DELAY_MS),
    "OTEL_BLRP_MAX_QUEUE_SIZE": ("Max queued log records", BLRP_MAX_QUEUE_SIZE),
    "OTEL_BLRP_MAX_EXPORT_BATCH_SIZE": ("Max log records per export batch", BLRP_MAX_EXPORT_BATCH_SIZE),
    "OTEL_BLRP_EXPORT_TIMEOUT": ("Log export timeout (ms)", BLRP_EXPORT_TIMEOUT_MS),
}


def get_batch_config_summary() -> Dict[str, Dict[str, Union[int, str, bool]]]:
    """Return the active batch processor configuration.

    Reads each known batch processor env var and reports its effective
    value (from environment or default) along with whether it was
    explicitly set.

    Returns:
        Dict keyed by env var name.  Each value is a dict with keys:
        - ``value``: the effective integer value
        - ``default``: the SDK default
        - ``description``: human-readable description
        - ``customized``: True if the env var was explicitly set
    """
    summary: Dict[str, Dict[str, Union[int, str, bool]]] = {}
    for env_var, (description, default) in _BATCH_ENV_VARS.items():
        raw = os.environ.get(env_var)
        if raw is not None:
            try:
                value = int(raw)
            except ValueError:
                value = default
            customized = True
        else:
            value = default
            customized = False
        summary[env_var] = {
            "value": value,
            "default": default,
            "description": description,
            "customized": customized,
        }
    return summary


def log_batch_config() -> None:
    """Log the active batch processor configuration at INFO level.

    Useful at application startup to record the effective settings in
    structured logs for later debugging of export issues.
    """
    summary = get_batch_config_summary()
    customized = {k: v for k, v in summary.items() if v["customized"]}

    if customized:
        logger.info(
            "OTel batch processor config (customized): %s",
            {k: v["value"] for k, v in customized.items()},
        )
    else:
        logger.info(
            "OTel batch processor config: all defaults "
            "(BSP delay=%dms, queue=%d, batch=%d, timeout=%dms)",
            BSP_SCHEDULE_DELAY_MS,
            BSP_MAX_QUEUE_SIZE,
            BSP_MAX_EXPORT_BATCH_SIZE,
            BSP_EXPORT_TIMEOUT_MS,
        )
