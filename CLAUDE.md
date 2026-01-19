# CLAUDE.md

This file provides guidance to Claude Code for the ContextCore project.

## Project Summary

**ContextCore** is a project management observability framework that models project tasks as OpenTelemetry spans. It eliminates manual status reporting by deriving project health from existing artifact metadata (commits, PRs, CI results) and exports via OTLP to any compatible backend.

**Core insight**: Tasks share the same structure as distributed trace spans—start time, end time, status, hierarchy, events. By storing tasks in observability infrastructure, you get unified querying, time-series persistence, and correlation with runtime telemetry.

## Tech Stack

- **Language**: Python 3.9+
- **CRD Framework**: kopf (Kubernetes Operator Framework)
- **Telemetry**: OpenTelemetry SDK, OTLP export
- **Reference Backend**: Grafana (Tempo, Mimir, Loki)
- **CLI**: Click
- **Models**: Pydantic v2

## Project Structure

```
ContextCore/
├── src/contextcore/
│   ├── __init__.py
│   ├── models.py            # Pydantic models for CRD spec
│   ├── tracker.py           # TaskTracker (tasks as spans)
│   ├── state.py             # Span state persistence
│   ├── metrics.py           # Derived project metrics
│   ├── logger.py            # TaskLogger (structured logs)
│   ├── detector.py          # OTel Resource Detector
│   ├── cli.py               # CLI interface
│   ├── dashboards/          # Dashboard provisioning
│   │   ├── __init__.py
│   │   ├── provisioner.py   # Grafana API dashboard provisioning
│   │   ├── portfolio.json   # Portfolio Overview dashboard JSON
│   │   └── project.json     # Project Details dashboard JSON
│   ├── agent/               # Agent communication layer
│   │   ├── insights.py      # InsightEmitter, InsightQuerier
│   │   ├── guidance.py      # GuidanceReader
│   │   ├── handoff.py       # Agent-to-agent handoffs
│   │   └── personalization.py
│   ├── skill/               # Skill telemetry
│   └── demo/                # Demo data generation
├── crds/
│   └── projectcontext.yaml  # CRD definition
├── helm/contextcore/        # Helm chart
├── docs/
│   ├── semantic-conventions.md
│   ├── agent-semantic-conventions.md
│   ├── agent-communication-protocol.md
│   └── dashboards/          # Dashboard specifications
│       ├── PROJECT_PORTFOLIO_OVERVIEW.md
│       └── PROJECT_DETAILS.md
└── tests/
```

## System Requirements

**Python Command**: This system only has `python3`, not `python`. Always use:
- `python3` instead of `python`
- `pip3` instead of `pip`
- `python3 -m module` instead of `python -m module`

## Commands

```bash
# Install
pip3 install -e ".[dev]"

# Run tests
python3 -m pytest

# Type checking
mypy src/contextcore

# Linting
ruff check src/
black src/

# CLI usage
contextcore task start --id PROJ-123 --title "Feature" --type story
contextcore task update --id PROJ-123 --status in_progress
contextcore task complete --id PROJ-123
contextcore sprint start --id sprint-3 --name "Sprint 3"
contextcore metrics summary --project my-project

# Dashboard provisioning
contextcore dashboards provision                    # Auto-detect Grafana
contextcore dashboards provision --grafana-url URL  # Explicit Grafana URL
contextcore dashboards provision --dry-run          # Preview without applying
contextcore dashboards list                         # Show provisioned dashboards
contextcore dashboards delete                       # Remove ContextCore dashboards
```

## Key Patterns

### Tasks as Spans

```python
from contextcore import TaskTracker

tracker = TaskTracker(project="my-project")
tracker.start_task(task_id="PROJ-123", title="Implement auth", task_type="story")
tracker.update_status("PROJ-123", "in_progress")  # Adds span event
tracker.complete_task("PROJ-123")  # Ends span
```

### Agent Insights

```python
from contextcore.agent import InsightEmitter, InsightQuerier

# Emit insights (stored as spans in Tempo)
emitter = InsightEmitter(project_id="checkout", agent_id="claude")
emitter.emit_decision("Selected event-driven architecture", confidence=0.92)

# Query insights from other agents
querier = InsightQuerier()
decisions = querier.query(project_id="checkout", insight_type="decision")
```

### ProjectContext CRD

```yaml
apiVersion: contextcore.io/v1
kind: ProjectContext
metadata:
  name: checkout-service
  namespace: commerce
spec:
  project:
    id: "commerce-platform"
    epic: "EPIC-42"
  business:
    criticality: critical
    owner: commerce-team
  requirements:
    availability: "99.95"
    latencyP99: "200ms"
  observability:
    traceSampling: 1.0
    alertChannels: ["commerce-oncall"]
```

## Environment Variables

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=contextcore
KUBECONFIG=~/.kube/config
```

## Must Do

- Use ProjectContext CRD as the source of truth for project metadata
- Derive observability config from business metadata (criticality → sampling rate)
- Include context in all generated artifacts (alerts, dashboards)
- Validate CRD schema strictly with Pydantic
- Export via OTLP (vendor-agnostic)
- **Provision dashboards on install**: ContextCore must auto-provision the Project Portfolio Overview and Project Details dashboards to Grafana during installation
- Dashboard provisioning must be idempotent (safe to run multiple times)
- Dashboards must use ContextCore semantic conventions for all queries

## Must Avoid

- Duplicating context in multiple places
- Manual annotation of K8s resources (use controller)
- Storing sensitive data in ProjectContext
- Over-generating artifacts (derive only what's needed)
- Vendor-specific code in core SDK

## Session Context (Dogfooding)

This project uses its own patterns for agent memory. ContextCore manages ContextCore.

### Query Prior Context

Before significant decisions, check what's been decided:

```python
from contextcore.agent import InsightQuerier

querier = InsightQuerier()
prior_decisions = querier.query(
    project_id="contextcore",
    insight_type="decision",
    time_range="30d"
)

# Check for lessons learned about specific files
lessons = querier.query(
    project_id="contextcore",
    insight_type="lesson",
    applies_to="src/contextcore/tracker.py"
)
```

### Emit Insights

After making decisions or learning something, persist for future sessions:

```python
from contextcore.agent import InsightEmitter

emitter = InsightEmitter(project_id="contextcore", agent_id="claude")

# Emit a decision
emitter.emit_decision(
    summary="Chose X over Y because Z",
    confidence=0.9,
    context={"file": "relevant/file.py"}
)

# Emit a lesson learned
emitter.emit_lesson(
    summary="Always mock OTLP exporter in unit tests",
    category="testing",
    applies_to=["src/contextcore/tracker.py"]
)
```

### Check Human Guidance

Query for constraints and open questions set by humans:

```python
from contextcore.agent import GuidanceReader

reader = GuidanceReader(project_id="contextcore")
constraints = reader.get_active_constraints()
questions = reader.get_open_questions()
```

## Documentation

- [README.md](README.md) — Vision, benefits, quick start
- [CLAUDE-full.md](CLAUDE-full.md) — Extended documentation with diagrams
- [docs/semantic-conventions.md](docs/semantic-conventions.md) — Full attribute reference
- [docs/agent-semantic-conventions.md](docs/agent-semantic-conventions.md) — Agent attributes
- [docs/agent-communication-protocol.md](docs/agent-communication-protocol.md) — Agent integration
- [docs/dashboards/PROJECT_PORTFOLIO_OVERVIEW.md](docs/dashboards/PROJECT_PORTFOLIO_OVERVIEW.md) — Portfolio dashboard spec
- [docs/dashboards/PROJECT_DETAILS.md](docs/dashboards/PROJECT_DETAILS.md) — Project details dashboard spec
