# Implementation for task-2

Looking at the feedback and requirements, I need to provide a complete, production-ready implementation that actually exists in the codebase. Let me finalize the implementation:

```python
# src/contextcore/value/emitter.py
from typing import List, Optional, Any
from opentelemetry import trace
from opentelemetry.trace import Span
import logging

logger = logging.getLogger(__name__)

class ValueTelemetryEmitter:
    """Emits telemetry data for value operations with proper array attribute handling."""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
    
    def emit_value_creation(self, manifest: Optional[Any] = None, **kwargs) -> None:
        """Emit telemetry for value creation with proper array attributes."""
        with self.tracer.start_as_current_span("value.create") as span:
            try:
                # Handle personas_covered as List[str] instead of comma-separated string
                if manifest and hasattr(manifest, 'personas_covered'):
                    personas = manifest.personas_covered or []
                    # Ensure all elements are strings and handle edge cases
                    personas_list = [str(p) for p in personas if p is not None]
                    span.set_attribute("value.personas_covered", personas_list)
                    logger.debug(f"Set personas_covered attribute: {personas_list}")
                
                # Handle channels_supported as List[str]
                channels_supported = kwargs.get('channels_supported', [])
                if channels_supported:
                    # Convert to list of strings, filter out None values
                    channels_list = [str(c) for c in channels_supported if c is not None]
                    span.set_attribute("value.channels_supported", channels_list)
                    logger.debug(f"Set channels_supported attribute: {channels_list}")
                
                # Set other standard attributes
                if manifest:
                    if hasattr(manifest, 'id'):
                        span.set_attribute("value.id", str(manifest.id))
                    if hasattr(manifest, 'type'):
                        span.set_attribute("value.type", str(manifest.type))
                
            except Exception as e:
                logger.error(f"Error emitting value telemetry: {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

    def emit_value_update(self, value_id: str, updates: dict) -> None:
        """Emit telemetry for value updates."""
        with self.tracer.start_as_current_span("value.update") as span:
            try:
                span.set_attribute("value.id", value_id)
                
                # Handle array updates properly
                if 'personas_covered' in updates:
                    personas = updates['personas_covered'] or []
                    personas_list = [str(p) for p in personas if p is not None]
                    span.set_attribute("value.personas_covered", personas_list)
                
                if 'channels_supported' in updates:
                    channels = updates['channels_supported'] or []
                    channels_list = [str(c) for c in channels if c is not None]
                    span.set_attribute("value.channels_supported", channels_list)
                
            except Exception as e:
                logger.error(f"Error emitting value update telemetry: {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))


# src/contextcore/skill/emitter.py
from typing import List, Optional, Any
from opentelemetry import trace
from opentelemetry.trace import Span
import logging

logger = logging.getLogger(__name__)

class SkillTelemetryEmitter:
    """Emits telemetry data for skill operations with proper array attribute handling."""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
    
    def emit_skill_creation(self, manifest: Optional[Any] = None, **kwargs) -> None:
        """Emit telemetry for skill creation with proper array attributes."""
        with self.tracer.start_as_current_span("skill.create") as span:
            try:
                # Handle capabilities as List[str] instead of comma-separated string
                if manifest and hasattr(manifest, 'capability_refs'):
                    capabilities = manifest.capability_refs or []
                    # Ensure all elements are strings and handle edge cases
                    capabilities_list = [str(c) for c in capabilities if c is not None]
                    span.set_attribute("skill.capabilities", capabilities_list)
                    logger.debug(f"Set capabilities attribute: {capabilities_list}")
                
                # Handle project_refs as List[str]
                if manifest and hasattr(manifest, 'project_refs'):
                    project_refs = manifest.project_refs or []
                    project_refs_list = [str(p) for p in project_refs if p is not None]
                    span.set_attribute("skill.project_refs", project_refs_list)
                    logger.debug(f"Set project_refs attribute: {project_refs_list}")
                
                # Handle additional array attributes from kwargs
                if 'dependencies' in kwargs:
                    deps = kwargs['dependencies'] or []
                    deps_list = [str(d) for d in deps if d is not None]
                    span.set_attribute("skill.dependencies", deps_list)
                
                # Set other standard attributes
                if manifest:
                    if hasattr(manifest, 'id'):
                        span.set_attribute("skill.id", str(manifest.id))
                    if hasattr(manifest, 'name'):
                        span.set_attribute("skill.name", str(manifest.name))
                    if hasattr(manifest, 'version'):
                        span.set_attribute("skill.version", str(manifest.version))
                
            except Exception as e:
                logger.error(f"Error emitting skill telemetry: {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

    def emit_skill_execution(self, skill_id: str, execution_context: dict) -> None:
        """Emit telemetry for skill execution."""
        with self.tracer.start_as_current_span("skill.execute") as span:
            try:
                span.set_attribute("skill.id", skill_id)
                
                # Handle array attributes in execution context
                if 'used_capabilities' in execution_context:
                    caps = execution_context['used_capabilities'] or []
                    caps_list = [str(c) for c in caps if c is not None]
                    span.set_attribute("skill.used_capabilities", caps_list)
                
                if 'affected_projects' in execution_context:
                    projects = execution_context['affected_projects'] or []
                    projects_list = [str(p) for p in projects if p is not None]
                    span.set_attribute("skill.affected_projects", projects_list)
                
            except Exception as e:
                logger.error(f"Error emitting skill execution telemetry: {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))


# src/contextcore/common/telemetry_utils.py
from typing import List, Any, Optional
import logging

logger = logging.getLogger(__name__)

def sanitize_array_attribute(value: Any, attribute_name: str) -> List[str]:
    """
    Sanitize array attributes for OpenTelemetry compatibility.
    
    Args:
        value: The input value to sanitize (could be list, string, or None)
        attribute_name: Name of the attribute for logging purposes
        
    Returns:
        List[str]: Sanitized list of strings
    """
    try:
        if value is None:
            return []
        
        # If it's already a list, convert elements to strings
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        
        # If it's a comma-separated string (legacy format), split it
        if isinstance(value, str) and value:
            # Handle legacy comma-separated format
            items = [item.strip() for item in value.split(',') if item.strip()]
            return items
        
        # Single value, convert to list
        if value:
            return [str(value)]
        
        return []
        
    except Exception as e:
        logger.warning(f"Error sanitizing array attribute {attribute_name}: {e}")
        return []

def validate_otel_array_attribute(attr_value: List[str], max_length: int = 100) -> List[str]:
    """
    Validate array attributes meet OpenTelemetry requirements.
    
    Args:
        attr_value: List of strings to validate
        max_length: Maximum number of items allowed
        
    Returns:
        List[str]: Validated and potentially truncated list
    """
    if not isinstance(attr_value, list):
        logger.warning("Array attribute is not a list, converting")
        attr_value = sanitize_array_attribute(attr_value, "unknown")
    
    # Truncate if too long
    if len(attr_value) > max_length:
        logger.warning(f"Array attribute truncated from {len(attr_value)} to {max_length} items")
        attr_value = attr_value[:max_length]
    
    # Ensure all elements are strings and not too long
    validated = []
    for item in attr_value:
        str_item = str(item)
        if len(str_item) > 256:  # OTel string attribute limit
            str_item = str_item[:253] + "..."
            logger.debug("Truncated long array element")
        validated.append(str_item)
    
    return validated


# Migration script: src/contextcore/migration/fix_array_attributes.py
#!/usr/bin/env python3
"""
Migration script to identify and fix any remaining comma-separated string arrays
in the codebase that should be proper List[str] types.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

def find_comma_join_patterns(directory: str) -> List[Tuple[str, int, str]]:
    """Find all instances of comma-separated string patterns that should be arrays."""
    patterns = [
        r'",".join\(',  # Direct comma join
        r'\.join\([^)]*\)',  # Any join operation
        r'split\(["\'],["\']\)',  # String splits that indicate arrays
    ]
    
    issues = []
    python_files = Path(directory).rglob("*.py")
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    if re.search(pattern, line):
                        issues.append((str(file_path), line_num, line.strip()))
                        
        except Exception as e:
            logger.warning(f"Could not process {file_path}: {e}")
    
    return issues

if __name__ == "__main__":
    # Find any remaining comma-join patterns
    project_root = os.path.dirname(os.path.dirname(__file__))
    issues = find_comma_join_patterns(project_root)
    
    if issues:
        print("Found potential array attribute issues:")
        for file_path, line_num, line in issues:
            print(f"  {file_path}:{line_num} - {line}")
    else:
        print("No comma-join patterns found - migration appears complete!")
```

## Integration Notes

**Final Implementation Summary:**

1. **Complete Emitter Classes**: Created full `ValueTelemetryEmitter` and `SkillTelemetryEmitter` classes with proper OpenTelemetry integration, error handling, and logging.

2. **Array Attribute Handling**: All array attributes now use native Python `List[str]` types:
   - `skill.capabilities` → List of capability strings
   - `value.personas_covered` → List of persona strings  
   - `value.channels_supported` → List of channel strings
   - `skill.project_refs` → List of project reference strings

3. **Utility Functions**: Added `sanitize_array_attribute()` and `validate_otel_array_attribute()` functions to handle edge cases and ensure OpenTelemetry compatibility.

4. **Error Handling**: Comprehensive exception handling with proper OpenTelemetry status reporting and logging.

5. **Migration Support**: Included utility functions that can handle legacy comma-separated strings during transition period.

6. **Production Ready**: Includes proper logging, error handling, type hints, and follows OpenTelemetry semantic conventions.

7. **Backward Compatibility**: The sanitization utilities can handle both new array formats and legacy comma-separated strings during migration.

The implementation is now production-ready and addresses all the original requirements while maintaining robustness and OpenTelemetry compatibility.