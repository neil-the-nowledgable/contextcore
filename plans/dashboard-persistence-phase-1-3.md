# Dashboard & Persistence: Phases 1-3

## Overview
Foundation phases: Dashboard folder structure, Grafana multi-provider config, and discovery module.

---

## Phase 1: Dashboard Folder Structure

### Objective
Reorganize dashboards from flat `json/` folder into extension-specific folders.

### Tasks

| ID | Title | Type | Description |
|----|-------|------|-------------|
| DP-001 | Create core dashboard folder | task | Create `grafana/provisioning/dashboards/core/` directory |
| DP-002 | Create extension folders | task | Create folders for squirrel, rabbit, beaver, fox, coyote, external |
| DP-003 | Move core dashboards | task | Move portfolio, installation, project-progress, project-operations, sprint-metrics to core/ |
| DP-004 | Move squirrel dashboards | task | Move skills-browser, value-capabilities to squirrel/ |
| DP-005 | Move rabbit dashboards | task | Move workflow.json to rabbit/ |
| DP-006 | Move external dashboards | task | Move agent-trigger.json to external/ |
| DP-007 | Update dashboard UIDs | task | Rename UIDs to contextcore-{extension}-{name} format |

### Deliverables
- [ ] Folder structure created
- [ ] All 9 dashboards moved to correct locations
- [ ] UIDs updated in JSON files

---

## Phase 2: Grafana Multi-Provider Config

### Objective
Update Grafana provisioning to auto-load from multiple extension folders.

### Tasks

| ID | Title | Type | Description |
|----|-------|------|-------------|
| DP-008 | Backup existing dashboards.yaml | task | Copy current config to dashboards.yaml.bak |
| DP-009 | Create multi-provider config | task | Write new dashboards.yaml with provider per extension |
| DP-010 | Configure core provider | task | Add provider for ContextCore folder, path: /etc/.../core |
| DP-011 | Configure squirrel provider | task | Add provider for ContextCore / Squirrel folder |
| DP-012 | Configure rabbit provider | task | Add provider for ContextCore / Rabbit folder |
| DP-013 | Configure remaining providers | task | Add beaver, fox, coyote, external providers |
| DP-014 | Test Grafana reload | task | Restart Grafana, verify all dashboards appear in correct folders |

### Deliverables
- [ ] New dashboards.yaml with 7 providers
- [ ] All dashboards visible in Grafana
- [ ] Correct folder hierarchy in Grafana UI

---

## Phase 3: Discovery Module

### Objective
Create Python module for auto-discovering dashboards from filesystem and entry points.

### Tasks

| ID | Title | Type | Description |
|----|-------|------|-------------|
| DP-015 | Create discovery.py module | story | New file: src/contextcore/dashboards/discovery.py |
| DP-016 | Implement EXTENSION_REGISTRY | task | Define registry mapping extension IDs to folder names/UIDs |
| DP-017 | Extend DashboardConfig | task | Add `extension` and `file_path` fields to dataclass |
| DP-018 | Implement discover_from_filesystem | task | Function to scan folders and parse JSON metadata |
| DP-019 | Implement discover_from_entry_points | task | Function to load from Python entry points |
| DP-020 | Implement discover_all_dashboards | task | Combine both sources with deduplication |
| DP-021 | Implement list_extensions | task | Function to list available extensions with counts |
| DP-022 | Add unit tests | task | Test discovery with mock filesystem and entry points |

### Deliverables
- [ ] `discovery.py` module complete
- [ ] All 6 functions implemented
- [ ] Unit tests passing

---

## Acceptance Criteria

1. `ls grafana/provisioning/dashboards/` shows: core/, squirrel/, rabbit/, beaver/, fox/, coyote/, external/
2. Grafana UI shows folders: ContextCore, ContextCore / Squirrel, ContextCore / Rabbit, etc.
3. `python -c "from contextcore.dashboards.discovery import discover_all_dashboards; print(len(discover_all_dashboards()))"` returns 9
