# ContextCore Dashboard Catalog

A comprehensive catalog of all Grafana dashboard JSON files in the ContextCore project.

---

## Primary Location: `grafana/provisioning/dashboards/json/`

These are the canonical dashboards auto-provisioned to Grafana.

### 🔄 Task/Workflow Management

| File | Title | Description | UID |
|------|-------|-------------|-----|
| **`workflow.json`** ⭐ | **ContextCore Workflow Manager** | View project tasks and workflow executions from Tempo traces | `contextcore-workflow` |
| `beaver-lead-contractor-progress.json` | Lead Contractor Progress | Track project progress with task status and execution traces | `beaver-lead-contractor` |
| `project-progress.json` | Project Progress | Track epics, stories, and tasks as OpenTelemetry spans | - |
| `sprint-metrics.json` | Sprint Metrics | Track velocity, throughput, and sprint performance | - |

### 📊 Portfolio/Overview

| File | Title | Description | UID |
|------|-------|-------------|-----|
| `portfolio.json` | Portfolio Overview | Multi-project portfolio view | - |

### ⚙️ Operations & Infrastructure

| File | Title | Description | UID |
|------|-------|-------------|-----|
| `installation.json` | Installation Verification | Self-monitoring dashboard for installation completeness | - |
| `project-operations.json` | Project-to-Operations | Correlate project context with runtime telemetry | - |

### 🤖 Agent & Automation

| File | Title | Description | UID |
|------|-------|-------------|-----|
| `fox-alert-automation.json` | Fox Alert Automation | Alert context enrichment, criticality routing, and action telemetry | `fox-alert-automation` |
| `agent-trigger.json` | Claude Agent | Dashboard for triggering Claude agent from Grafana | - |

### 🎯 Skills & Capabilities

| File | Title | Description | UID |
|------|-------|-------------|-----|
| `skills-browser.json` | Skills Browser | Skills catalog browser | `skills-browser` |
| `value-capabilities.json` | Value Capabilities Explorer | Explore value capabilities and skills | `value-simple` |

---

## Other Locations

### `k8s/observability/dashboards/` (Kubernetes Deployment)

Copies of dashboards for Kubernetes ConfigMap deployment:

- `installation.json`
- `portfolio.json`
- `project-operations.json`
- `project-progress.json`
- `sprint-metrics.json`
- `value-capabilities.json`

### `demo/dashboards/` (Demo Data)

Dashboards bundled with demo scenarios:

- `project-operations.json`
- `project-progress.json`
- `sprint-metrics.json`

### `src/contextcore/dashboards/` (Python Package)

Embedded dashboards for programmatic provisioning:

- `installation.json`
- `portfolio.json`
- `value-capabilities.json`

### `docs/dashboards/` (Documentation)

- `languagemodel1oh-site-launch-contextcore.json` - Documentation example

### `plugins/contextcore-workflow-panel/` (Grafana Plugin)

- `plugin.json` - Plugin manifest (not a dashboard)

---

## Quick Reference: Task Workflow Management

**Looking for a task/workflow management dashboard?**

Use: `grafana/provisioning/dashboards/json/workflow.json`

**ContextCore Workflow Manager** features:
- Project task overview from Tempo traces
- Workflow execution tracking
- Multi-project support via template variable
- 30-second auto-refresh
- 7-day default time range

**Access in Grafana:** `http://localhost:3000/d/contextcore-workflow`

---

## Dashboard Tags

| Tag | Dashboards |
|-----|------------|
| `contextcore` | All ContextCore dashboards |
| `rabbit` | workflow.json |
| `workflow` | workflow.json |
| `beaver` | beaver-lead-contractor-progress.json |
| `startd8` | beaver-lead-contractor-progress.json |
| `fox` | fox-alert-automation.json |
| `waagosh` | fox-alert-automation.json |
| `alerts` | fox-alert-automation.json |
| `skills` | skills-browser.json |
| `squirrel` | skills-browser.json |
| `value` | value-capabilities.json |
| `capabilities` | value-capabilities.json |
