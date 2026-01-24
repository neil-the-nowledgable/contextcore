# Dashboard & Persistence: Phases 7-9

## Overview
Protection phases: Pre-destroy warnings, telemetry export, and audit trail.

---

## Phase 7: Pre-Destroy Warning System

### Objective
Enhance `make destroy` with data inventory and export options.

### Tasks

| ID | Title | Type | Description |
|----|-------|------|-------------|
| DP-048 | Create persistence CLI | task | Create src/contextcore/cli/persistence.py |
| DP-049 | Implement inventory command | task | `contextcore persistence inventory` shows data sources |
| DP-050 | Add data-inventory Makefile target | task | New target that calls persistence inventory |
| DP-051 | Create pre-destroy-check target | task | Generate inventory before destruction |
| DP-052 | Update destroy target | task | Add interactive menu: export all, export dashboards, or proceed |
| DP-053 | Add backup-full target | task | New target that exports telemetry + dashboards |
| DP-054 | Format inventory output | task | Show sizes, retention, importance with colors |
| DP-055 | Show retention warnings | task | Highlight data approaching retention limits |

### Deliverables
- [ ] `make data-inventory` shows formatted data inventory
- [ ] `make destroy` shows options before proceeding
- [ ] Retention warnings displayed

---

## Phase 8: Telemetry Exporter

### Objective
Export actual trace, metric, and log data (not just dashboards).

### Tasks

| ID | Title | Type | Description |
|----|-------|------|-------------|
| DP-056 | Create exporter.py | story | New file: src/contextcore/persistence/exporter.py |
| DP-057 | Implement ExportResult dataclass | task | Model for export operation result |
| DP-058 | Implement TelemetryExporter class | task | Main exporter with configurable endpoints |
| DP-059 | Implement _export_traces | task | Export from Tempo via /api/search + /api/traces |
| DP-060 | Implement _export_metrics | task | Export from Mimir via Prometheus query_range API |
| DP-061 | Implement _export_logs | task | Export from Loki via LogQL query_range API |
| DP-062 | Implement export_all | task | Orchestrate all exports with time range |
| DP-063 | Add export CLI command | task | `contextcore persistence export -t 24h -o ./backups/` |
| DP-064 | Write export manifest | task | Include metadata: timestamp, counts, time range |
| DP-065 | Handle API errors gracefully | task | Continue on partial failures, report errors |

### Deliverables
- [ ] `contextcore persistence export -t 24h` creates backup directory
- [ ] traces.json, metrics.json, logs.json created
- [ ] manifest.json with export metadata

---

## Phase 9: Audit Trail

### Objective
Record all destructive operations for accountability and recovery.

### Tasks

| ID | Title | Type | Description |
|----|-------|------|-------------|
| DP-066 | Create audit.py | story | New file: src/contextcore/persistence/audit.py |
| DP-067 | Implement AuditEvent dataclass | task | Model for audit record |
| DP-068 | Implement AuditTrail class | task | Record and query audit events |
| DP-069 | Implement record method | task | Append event to ~/.contextcore/audit.log |
| DP-070 | Implement _emit_to_loki | task | Push audit event to Loki (best effort) |
| DP-071 | Implement list_events method | task | Query recent audit events |
| DP-072 | Add audit CLI command | task | `contextcore persistence audit` shows history |
| DP-073 | Integrate with destroy | task | Record audit event on destroy operations |
| DP-074 | Add timestamp and user info | task | Include hostname, username, timestamp |

### Deliverables
- [ ] Audit events recorded to ~/.contextcore/audit.log
- [ ] `contextcore persistence audit` shows history
- [ ] `make destroy` creates audit record

---

## Acceptance Criteria

1. `make data-inventory` displays:
   ```
   tempo         48.2 MB  retention=48h       importance=high
   mimir        102.4 MB  retention=unlimited importance=critical
   loki          31.5 MB  retention=7d        importance=high
   grafana        2.1 MB  retention=unlimited importance=medium
   ```

2. `make destroy` shows:
   ```
   OPTIONS:
     1. Export all telemetry data before destroy
     2. Export dashboards only (current behavior)
     3. Destroy without export
   Select option [1/2/3]:
   ```

3. `contextcore persistence export -t 1h` creates:
   ```
   backups/20260124-143000/
   ├── manifest.json
   ├── traces.json
   ├── metrics.json
   └── logs.json
   ```

4. `contextcore persistence audit` shows:
   ```
   2026-01-24 14:30:00  destroy  user@hostname  backup=yes  outcome=success
   ```

---

## Final Integration

After all phases complete:
1. Run `make full-setup` to start stack
2. Run `contextcore dashboards provision` to provision all dashboards
3. Run `contextcore persistence inventory` to verify detection
4. Run `make destroy` to test the new safety workflow
