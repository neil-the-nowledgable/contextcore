# Dashboard & Persistence: Phases 4-6

## Overview
Integration phases: Update provisioner to use discovery, enhance CLI, and create persistence detector.

---

## Phase 4: Provisioner Update

### Objective
Integrate the discovery module into the existing DashboardProvisioner.

### Tasks

| ID | Title | Type | Description |
|----|-------|------|-------------|
| DP-023 | Import discovery module | task | Add imports from discovery.py to provisioner.py |
| DP-024 | Remove DEFAULT_DASHBOARDS | task | Remove hardcoded list, use discovery instead |
| DP-025 | Update provision_all method | task | Add `extension` parameter, use discover_all_dashboards() |
| DP-026 | Update delete_all method | task | Use discovery to find dashboards to delete |
| DP-027 | Update _load_dashboard_json | task | Use config.effective_file_path instead of file_name |
| DP-028 | Add extension filtering | task | Filter discovered dashboards by extension parameter |
| DP-029 | Update provisioner tests | task | Test with mocked discovery results |

### Deliverables
- [ ] Provisioner uses discovery module
- [ ] DEFAULT_DASHBOARDS removed
- [ ] Extension filtering works

---

## Phase 5: CLI Enhancements

### Objective
Add extension filtering and new commands to dashboard CLI.

### Tasks

| ID | Title | Type | Description |
|----|-------|------|-------------|
| DP-030 | Add --extension flag to provision | task | Filter provisioning by extension |
| DP-031 | Add --extension flag to list | task | Filter listing by extension |
| DP-032 | Add --extension flag to delete | task | Filter deletion by extension |
| DP-033 | Add --source flag to list | task | Option to show local, grafana, or both |
| DP-034 | Create extensions command | task | New command: `contextcore dashboards extensions` |
| DP-035 | Group output by extension | task | Display dashboards grouped by extension in list |
| DP-036 | Update CLI help text | task | Add examples for new flags |

### Deliverables
- [ ] `contextcore dashboards provision -e squirrel` works
- [ ] `contextcore dashboards list --source local` works
- [ ] `contextcore dashboards extensions` shows all extensions

---

## Phase 6: Persistence Detector

### Objective
Create module to detect what data needs persistence and derive importance.

### Tasks

| ID | Title | Type | Description |
|----|-------|------|-------------|
| DP-037 | Create persistence module | task | Create src/contextcore/persistence/__init__.py |
| DP-038 | Create detector.py | story | Main detection logic file |
| DP-039 | Implement DataSource dataclass | task | Model for a persistent data source |
| DP-040 | Implement PersistenceManifest | task | Container for all detected sources |
| DP-041 | Implement _scan_docker_compose | task | Parse docker-compose.yaml for volumes |
| DP-042 | Implement _parse_tempo_retention | task | Extract retention from tempo/tempo.yaml |
| DP-043 | Implement _parse_loki_retention | task | Extract retention from loki/loki.yaml |
| DP-044 | Implement _scan_state_directory | task | Find ~/.contextcore/state/ files |
| DP-045 | Implement _derive_importance | task | Use .contextcore.yaml business criticality |
| DP-046 | Implement _generate_warnings | task | Create warnings for approaching retention |
| DP-047 | Add detector tests | task | Test with mock configs |

### Deliverables
- [ ] `persistence/` module created
- [ ] PersistenceDetector class complete
- [ ] Can generate manifest from project root

---

## Acceptance Criteria

1. `contextcore dashboards provision` provisions all 9 dashboards automatically
2. `contextcore dashboards provision -e core` only provisions 5 core dashboards
3. `contextcore dashboards extensions` lists 7 extensions with dashboard counts
4. `python -c "from contextcore.persistence import PersistenceDetector; d = PersistenceDetector('.'); print(len(d.detect().sources))"` returns 4+
