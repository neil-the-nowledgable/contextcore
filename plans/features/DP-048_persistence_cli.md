# Feature: DP-048 - Create Persistence CLI

## Overview
Add CLI commands for persistence detection and data inventory.

## Target Files
- `src/contextcore/cli/persistence.py` (new file)
- `src/contextcore/cli/__init__.py` (modify to register)

## Requirements

### Commands
```bash
# List all detected data sources
contextcore persistence inventory

# Show details for a specific source
contextcore persistence show <source_name>

# Export data before destroy
contextcore persistence export --output /backup/path

# Check what would be lost on destroy
contextcore persistence check-destroy
```

### Implementation
```python
"""Persistence CLI commands."""

import click
from pathlib import Path
from contextcore.persistence.detector import detect_all, DataSource

@click.group()
def persistence():
    """Manage persistent data sources."""
    pass

@persistence.command()
@click.option("--format", type=click.Choice(["table", "json"]), default="table")
def inventory(format: str):
    """List all detected data sources."""
    sources = detect_all(Path.cwd())
    if format == "json":
        # JSON output
        ...
    else:
        # Rich table output
        ...

@persistence.command()
def check_destroy():
    """Show what data would be lost on destroy."""
    sources = detect_all(Path.cwd())
    critical = [s for s in sources if s.importance == "critical"]
    if critical:
        click.echo("WARNING: Critical data would be lost:")
        for s in critical:
            click.echo(f"  - {s.name} ({s.type})")
```

## Acceptance Criteria
- [ ] `inventory` command lists sources
- [ ] `check-destroy` warns about critical data
- [ ] JSON output format supported
- [ ] Table output with Rich formatting
- [ ] Registered in main CLI

## Dependencies
- DP-038 (detector module)
- Click, Rich

## Size Estimate
~80 lines of code
