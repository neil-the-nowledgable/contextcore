# Feature: DP-056 - Create Telemetry Exporter Module

## Overview
Create an exporter module that can export traces, metrics, and logs from the observability stack for backup purposes.

## Target Files
- `src/contextcore/persistence/exporter.py` (new file)
- `src/contextcore/cli/persistence.py` (modify to add export command)

## Requirements

### Module Structure
```python
"""Export telemetry data from observability backends."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import httpx

@dataclass
class ExportConfig:
    """Configuration for export operation."""
    output_dir: Path
    time_range: timedelta = timedelta(hours=24)
    tempo_url: str = "http://localhost:3200"
    mimir_url: str = "http://localhost:9009"
    loki_url: str = "http://localhost:3100"

@dataclass
class ExportResult:
    """Result of an export operation."""
    traces_count: int
    metrics_count: int
    logs_count: int
    total_bytes: int
    output_files: List[Path]

async def export_traces(
    config: ExportConfig,
    service_filter: Optional[str] = None
) -> Path:
    """Export traces from Tempo.

    Uses:
    - GET /api/search to find trace IDs
    - GET /api/traces/{traceID} to fetch full traces
    """
    ...

async def export_metrics(
    config: ExportConfig,
    queries: Optional[List[str]] = None
) -> Path:
    """Export metrics from Mimir/Prometheus.

    Uses:
    - POST /api/v1/query_range for time series data
    """
    ...

async def export_logs(
    config: ExportConfig,
    query: str = '{job=~".+"}'
) -> Path:
    """Export logs from Loki.

    Uses:
    - GET /loki/api/v1/query_range for log entries
    """
    ...

async def export_all(config: ExportConfig) -> ExportResult:
    """Export all telemetry data."""
    ...
```

### CLI Integration
```python
@persistence.command()
@click.option("-t", "--time-range", default="24h", help="Time range to export")
@click.option("-o", "--output", type=click.Path(), default="./backups")
@click.option("--traces/--no-traces", default=True)
@click.option("--metrics/--no-metrics", default=True)
@click.option("--logs/--no-logs", default=True)
def export(time_range: str, output: str, traces: bool, metrics: bool, logs: bool):
    """Export telemetry data before destroy."""
    ...
```

## Acceptance Criteria
- [ ] Exports traces as JSON with full span data
- [ ] Exports metrics as Prometheus text format
- [ ] Exports logs as JSONL
- [ ] Time range filtering works
- [ ] Progress indicator during export
- [ ] Creates timestamped backup directory

## Dependencies
- DP-048 (persistence CLI base)
- httpx for async HTTP

## Size Estimate
~150 lines of code

