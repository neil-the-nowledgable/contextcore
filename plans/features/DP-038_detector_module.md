# Feature: DP-038 - Create Detector Module

## Overview
Create a detector module that identifies data sources with persistence in the observability stack.

## Target Files
- `src/contextcore/persistence/detector.py` (new file)

## Requirements

### Module Structure
```python
"""Detect persistent data sources in the observability stack."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional
import yaml

class DataSourceType(str, Enum):
    """Types of data sources."""
    PROMETHEUS = "prometheus"
    LOKI = "loki"
    TEMPO = "tempo"
    MIMIR = "mimir"
    POSTGRES = "postgres"
    SQLITE = "sqlite"

class Importance(str, Enum):
    """Data importance levels."""
    CRITICAL = "critical"  # Must backup before destroy
    HIGH = "high"          # Should backup
    MEDIUM = "medium"      # Nice to backup
    LOW = "low"            # Can regenerate

@dataclass
class DataSource:
    """A detected data source."""
    name: str
    type: DataSourceType
    path: Optional[Path]
    volume: Optional[str]
    importance: Importance
    size_bytes: Optional[int] = None

def scan_docker_compose(
    compose_path: Path
) -> List[DataSource]:
    """Scan docker-compose.yaml for data sources."""
    ...

def derive_importance(
    source: DataSource
) -> Importance:
    """Derive importance level for a data source."""
    ...

def detect_all(
    project_root: Path
) -> List[DataSource]:
    """Detect all data sources in project."""
    ...
```

## Acceptance Criteria
- [ ] DataSourceType enum with common types
- [ ] Importance enum with levels
- [ ] DataSource dataclass with all fields
- [ ] scan_docker_compose parses volumes
- [ ] derive_importance uses heuristics
- [ ] detect_all returns sorted by importance

## Dependencies
- PyYAML for docker-compose parsing

## Size Estimate
~120 lines of code
