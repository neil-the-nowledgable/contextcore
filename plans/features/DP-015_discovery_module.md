# Feature: DP-015 - Create Discovery Module

## Overview
Create a new discovery module that finds dashboards from filesystem and entry points.

## Target Files
- `src/contextcore/dashboards/discovery.py` (new file)

## Requirements

### Module Structure
```python
"""Dashboard discovery from filesystem and entry points."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
import importlib.metadata

@dataclass
class DiscoveredDashboard:
    """A discovered dashboard with metadata."""
    uid: str
    name: str
    path: Path
    source: str  # "filesystem" | "entry_point"
    extension: Optional[str] = None  # e.g., "squirrel", "rabbit"

# Registry of known extensions
EXTENSION_REGISTRY = {
    "contextcore-squirrel": "squirrel",
    "contextcore-rabbit": "rabbit",
    "contextcore-beaver": "beaver",
    "contextcore-fox": "fox",
    "contextcore-coyote": "coyote",
    "contextcore-owl": "owl",
}

def discover_from_filesystem(
    base_path: Path,
    pattern: str = "**/*.json"
) -> List[DiscoveredDashboard]:
    """Discover dashboards from filesystem."""
    ...

def discover_from_entry_points(
    group: str = "contextcore.dashboards"
) -> List[DiscoveredDashboard]:
    """Discover dashboards from installed packages."""
    ...

def discover_all(
    base_path: Optional[Path] = None
) -> List[DiscoveredDashboard]:
    """Discover all dashboards from all sources."""
    ...
```

## Acceptance Criteria
- [ ] DiscoveredDashboard dataclass defined
- [ ] EXTENSION_REGISTRY maps package names to extensions
- [ ] discover_from_filesystem finds JSON files
- [ ] discover_from_entry_points uses importlib.metadata
- [ ] discover_all combines both sources
- [ ] Deduplicates by UID

## Dependencies
None (new module)

## Size Estimate
~100 lines of code
