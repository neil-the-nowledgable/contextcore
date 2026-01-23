"""
Compatibility layer for OTel GenAI Semantic Conventions.

Handles dual-emission of legacy ContextCore attributes (agent.*) and
standard OTel GenAI attributes (gen_ai.*) during the migration period.
"""

import os
import logging
import warnings
from enum import Enum
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OtelEmitMode(Enum):
    """Emission mode for semantic conventions."""
    DUAL = "dual"      # Emit both legacy and new attributes (default)
    LEGACY = "legacy"  # Emit only legacy attributes
    OTEL = "otel"      # Emit only new attributes (target state)

def get_emit_mode() -> OtelEmitMode:
    """Get the current emission mode from environment."""
    mode_str = os.environ.get("CONTEXTCORE_OTEL_MODE", "dual").lower()
    try:
        return OtelEmitMode(mode_str)
    except ValueError:
        logger.warning(f"Invalid CONTEXTCORE_OTEL_MODE '{mode_str}', defaulting to DUAL")
        return OtelEmitMode.DUAL

class AttributeMapper:
    """
    Maps legacy ContextCore attributes to OTel GenAI conventions.
    """

    # Mapping: Legacy -> OTel
    MAPPING = {
        "agent.id": "gen_ai.agent.id",
        # agent.name isn't strictly legacy but new OTel attribute, we map implicit name usage if needed
        # agent.session_id migration
        "agent.session_id": "gen_ai.conversation.id",
        
        # Handoff mapping (Task 5)
        "handoff.capability_id": "gen_ai.tool.name",
        # handoff.inputs handled specially due to JSON requirement? 
        # For now direct mapping, implementation details handled in code
    }

    def __init__(self):
        self.mode = get_emit_mode()
        self._warned_keys = set()

    def map_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a dictionary of attributes and apply mappings based on current mode.
        
        Returns a new dictionary with mapped attributes.
        """
        if self.mode == OtelEmitMode.LEGACY:
            return attributes.copy()

        new_attrs = attributes.copy()
        
        for key, value in attributes.items():
            if key in self.MAPPING:
                otel_key = self.MAPPING[key]
                
                if self.mode == OtelEmitMode.DUAL:
                    new_attrs[otel_key] = value
                elif self.mode == OtelEmitMode.OTEL:
                    new_attrs[otel_key] = value
                    # Remove legacy key if strictly OTel mode
                    # NOTE: Be careful with removing keys that code might rely on reading back
                    # For now, we might keep legacy keys in memory but OTel export filters them?
                    # Or we assume this dict goes to the span.
                    del new_attrs[key]

        return new_attrs

    def get_otel_key(self, legacy_key: str) -> Optional[str]:
        """Get the OTel equivalent for a legacy key."""
        return self.MAPPING.get(legacy_key)

    def record_deprecation_usage(self, key: str):
        """Log a warning when a legacy attribute is accessed/used (if in strict mode)."""
        if self.mode == OtelEmitMode.OTEL and key in self.MAPPING:
            if key not in self._warned_keys:
                warnings.warn(
                    f"Accessing legacy attribute '{key}' in OTEL strict mode. "
                    f"Use '{self.MAPPING[key]}' instead.",
                    DeprecationWarning,
                    stacklevel=2
                )
                self._warned_keys.add(key)

# Global instance
mapper = AttributeMapper()
