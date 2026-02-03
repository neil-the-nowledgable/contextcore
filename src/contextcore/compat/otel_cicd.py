"""OTel CI/CD semantic conventions dual-emit layer.

Opt-in feature that adds OTel CI/CD pipeline attributes alongside existing
task.* attributes. Disabled by default.

Enable via:
  CONTEXTCORE_CICD_EMIT=true
  OTEL_SEMCONV_STABILITY_OPT_IN=cicd
"""

import os
from typing import Dict, Any

# Mapping from existing ContextCore attributes to OTel CI/CD semantic conventions
CICD_ATTRIBUTE_MAPPINGS: Dict[str, str] = {
    "project.name": "cicd.pipeline.name",
    "sprint.id": "cicd.pipeline.run.id",
    "task.title": "cicd.pipeline.task.name",
    "task.id": "cicd.pipeline.task.run.id",
    "task.type": "cicd.pipeline.task.type",
}

_cached_enabled: bool | None = None


def get_cicd_emit_enabled() -> bool:
    """Check whether CI/CD dual-emit is enabled.

    Resolution order:
    1. CONTEXTCORE_CICD_EMIT env var (explicit, project-specific)
    2. OTEL_SEMCONV_STABILITY_OPT_IN contains "cicd" token
    3. Default: False (disabled)
    """
    global _cached_enabled
    if _cached_enabled is not None:
        return _cached_enabled

    # 1. ContextCore-specific env var takes precedence
    cc_cicd = os.getenv("CONTEXTCORE_CICD_EMIT", "").strip().lower()
    if cc_cicd:
        _cached_enabled = cc_cicd in ("true", "1", "yes")
        return _cached_enabled

    # 2. OTel standard env var (comma-separated token list)
    otel_opt_in = os.getenv("OTEL_SEMCONV_STABILITY_OPT_IN", "").strip().lower()
    if otel_opt_in:
        tokens = {t.strip() for t in otel_opt_in.split(",")}
        if "cicd" in tokens:
            _cached_enabled = True
            return _cached_enabled

    # 3. Default: disabled
    _cached_enabled = False
    return _cached_enabled


def apply_cicd_attributes(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Add CI/CD semantic convention attributes when enabled.

    When enabled, copies the dict and adds cicd.pipeline.* keys for any
    matching source keys. When disabled, returns input as-is (no copy).
    """
    if not get_cicd_emit_enabled():
        return attributes

    result = dict(attributes)
    for source_key, cicd_key in CICD_ATTRIBUTE_MAPPINGS.items():
        if source_key in result:
            result[cicd_key] = result[source_key]
    return result


def reset_cache() -> None:
    """Reset the cached enabled state. For test isolation."""
    global _cached_enabled
    _cached_enabled = None
