# Feature: DP-066 - Create Audit Trail Module

## Overview
Create an audit module to record all destructive operations for accountability and compliance.

## Target Files
- `src/contextcore/persistence/audit.py` (new file)
- `src/contextcore/cli/persistence.py` (modify to add audit command)
- `Makefile` (modify destroy target)

## Requirements

### Module Structure
```python
"""Audit trail for destructive operations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import os

class AuditOperation(str, Enum):
    """Types of audited operations."""
    DESTROY = "destroy"
    EXPORT = "export"
    PRUNE = "prune"
    DELETE_DASHBOARD = "delete_dashboard"

class AuditOutcome(str, Enum):
    """Operation outcomes."""
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"

@dataclass
class AuditEvent:
    """A recorded audit event."""
    timestamp: datetime
    operation: AuditOperation
    outcome: AuditOutcome
    user: str
    details: Dict[str, Any] = field(default_factory=dict)
    data_affected: List[str] = field(default_factory=list)
    export_path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "operation": self.operation.value,
            "outcome": self.outcome.value,
            "user": self.user,
            "details": self.details,
            "data_affected": self.data_affected,
            "export_path": str(self.export_path) if self.export_path else None
        }

class AuditLog:
    """Persistent audit log manager."""

    def __init__(self, log_path: Path = Path(".contextcore/audit.jsonl")):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: AuditEvent) -> None:
        """Append event to audit log."""
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def get_history(
        self,
        operation: Optional[AuditOperation] = None,
        limit: int = 50
    ) -> List[AuditEvent]:
        """Retrieve audit history."""
        ...

def get_current_user() -> str:
    """Get current user for audit records."""
    return os.environ.get("USER", "unknown")
```

### CLI Integration
```python
@persistence.command()
@click.option("-n", "--limit", default=20, help="Number of events to show")
@click.option("--operation", type=click.Choice(["destroy", "export", "prune"]))
def audit(limit: int, operation: Optional[str]):
    """Show audit history of destructive operations."""
    ...
```

### Makefile Integration
```makefile
destroy: data-inventory
	@echo "Recording audit event..."
	@python -c "from contextcore.persistence.audit import AuditLog, AuditEvent, AuditOperation; ..."
	docker compose down -v
```

## Acceptance Criteria
- [ ] AuditEvent dataclass with all fields
- [ ] AuditLog persists to .contextcore/audit.jsonl
- [ ] audit CLI command shows history
- [ ] destroy target records audit event
- [ ] User captured from environment
- [ ] Timestamps in ISO format

## Dependencies
- DP-048 (persistence CLI base)
- DP-056 (exporter for export_path reference)

## Size Estimate
~120 lines of code

