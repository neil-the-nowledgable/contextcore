# ADR-001: Model Tasks as OpenTelemetry Spans

**Status:** Accepted
**Date:** 2026-01-01 (retroactively documented 2026-01-28)
**Author:** Neil Yashinsky
**Confidence:** 0.95

---

## Context

Project management and observability have traditionally been separate domains:

- **Project management** lives in Jira, Linear, Notion—tools optimized for human workflows
- **Observability** lives in Grafana, Datadog, Prometheus—tools optimized for system telemetry

This separation creates friction:

1. **Status updates are manual** — Humans must translate work into status reports
2. **Debugging lacks business context** — Traces don't know which project or sprint they belong to
3. **Agent memory is ephemeral** — LLM agents forget what they learned between sessions
4. **Onboarding requires archaeology** — Understanding a system means reading stale docs

The question: Is there a unified model that could bridge these domains?

---

## Decision

**Model project tasks as OpenTelemetry spans.**

Tasks and spans share the same fundamental structure:

| Task Attribute | Span Attribute |
|---------------|----------------|
| Start time | Start timestamp |
| End time | End timestamp |
| Status (todo/in-progress/done) | Status (OK/ERROR) |
| Parent task | Parent span |
| Subtasks | Child spans |
| Events (comments, updates) | Span events |
| Metadata (assignee, labels) | Span attributes |

By storing tasks in observability infrastructure (Tempo, Loki, Mimir), we get:

- **Unified querying** — TraceQL for tasks, not just traces
- **Time-series persistence** — Task history without a separate database
- **Correlation** — Link runtime traces to the tasks that produced them
- **Agent memory** — Insights stored as spans, queryable across sessions

---

## Architecture

### Dual-Telemetry Emission

Tasks emit to both Tempo and Loki:

```
TaskTracker
    │
    ├──► Tempo (spans)
    │    - Hierarchy and timing
    │    - TraceQL queries
    │    - Parent-child relationships
    │
    └──► Loki (structured logs)
         - Status change events
         - Metrics derivation via recording rules
         - Full-text search
```

Mimir metrics are derived from Loki logs, not directly emitted.

### Task Lifecycle

```python
from contextcore import TaskTracker

tracker = TaskTracker(project="my-project")

# Start a task (creates span)
tracker.start_task(
    task_id="PROJ-123",
    title="Implement auth",
    task_type="story"
)

# Update status (adds span event)
tracker.update_status("PROJ-123", "in_progress")

# Complete task (ends span)
tracker.complete_task("PROJ-123")
```

### Agent Insights as Spans

```python
from contextcore.agent import InsightEmitter

emitter = InsightEmitter(project_id="checkout", agent_id="claude")

# Decision stored as span in Tempo
emitter.emit_decision(
    summary="Selected event-driven architecture",
    confidence=0.92,
    context={"alternatives_considered": ["REST", "GraphQL"]}
)
```

---

## Consequences

### Positive

1. **Unified infrastructure** — No separate task database; observability stack is the database
2. **Time-range queries** — "Show me all tasks from last sprint" uses standard TraceQL
3. **Agent memory** — Insights persist across sessions, queryable by future agents
4. **Correlation** — Runtime traces can reference the task that produced them
5. **Vendor independence** — OTLP export works with any compatible backend

### Neutral

1. **Learning curve** — Teams must understand spans to understand tasks
2. **Observability stack required** — Need Tempo/Loki/Grafana (or equivalents) running

### Negative

1. **Not a traditional PM tool** — Won't replace Jira for teams that need Jira's workflow features
2. **Retention limits** — Task history limited by Tempo/Loki retention policies
3. **Query complexity** — TraceQL is powerful but not as intuitive as SQL for simple queries

---

## Alternatives Considered

### 1. Separate Task Database

Store tasks in PostgreSQL/MongoDB, export metrics to observability.

**Rejected because:**
- Requires syncing between systems
- Loses unified querying
- Adds infrastructure complexity

### 2. Extend Existing PM Tools

Add observability integration to Jira/Linear.

**Rejected because:**
- Vendor lock-in
- Limited by PM tool's data model
- Can't store agent insights

### 3. Custom Task Service

Build a purpose-built task service with its own storage.

**Rejected because:**
- Reinventing observability infrastructure
- More code to maintain
- Doesn't leverage existing Grafana investment

---

## Validation

This decision has been validated through:

1. **Demo data generation** — HistoricalTaskTracker successfully emits backdated spans
2. **Dashboard queries** — Portfolio dashboard queries tasks via TraceQL
3. **Agent insights** — InsightEmitter/InsightQuerier work across sessions
4. **Dogfooding** — ContextCore manages ContextCore using this pattern

---

## References

- [OpenTelemetry Trace Specification](https://opentelemetry.io/docs/specs/otel/trace/)
- [docs/semantic-conventions.md](../semantic-conventions.md) — ContextCore attribute conventions
- [docs/agent-communication-protocol.md](../agent-communication-protocol.md) — Agent insight protocol
