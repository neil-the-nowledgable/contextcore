# GitHub Issue: Proposed Semantic Conventions - Project Management Namespace

> **Repository**: `open-telemetry/semantic-conventions`
> **Type**: Feature Request / Namespace Proposal
> **Status**: Draft - Ready for Submission

---

## Issue Title

```
[Feature] Add project.*, task.*, sprint.* semantic conventions for project management telemetry
```

## Issue Body

### Summary

Propose adding semantic conventions for project management telemetry, enabling organizations to model tasks as spans and derive project health from observability infrastructure.

### Motivation

Project management data (tasks, sprints, progress) and runtime telemetry live in separate silos. By modeling tasks with OTel semantic conventions:

1. **Unified Querying**: Query tasks via TraceQL alongside runtime traces
2. **Correlation**: Link production incidents to the tasks that introduced them
3. **Automation**: Derive task status from commits, PRs, CI results
4. **Portability**: Standard vocabulary works with any OTLP backend

### Use Cases

1. **Portfolio Dashboard**: `count by (project.id) (task_status{status="blocked"})`
2. **Incident Correlation**: Find task that introduced a bug via `project.id` join
3. **Velocity Tracking**: `sum by (sprint.id) (task_story_points{status="done"})`
4. **Blocked Work Alert**: `{ task.status = "blocked" && task.blocked_duration > 24h }`

### Proposed Attributes

#### `project.*` Namespace

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `project.id` | string | Unique project identifier | `"commerce-platform"` |
| `project.name` | string | Human-readable project name | `"Commerce Platform"` |
| `project.epic` | string | Parent epic/initiative identifier | `"EPIC-42"` |

#### `task.*` Namespace

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `task.id` | string | Unique task identifier | `"PROJ-123"` |
| `task.type` | enum | Task hierarchy type | `epic`, `story`, `task`, `subtask`, `bug`, `spike` |
| `task.title` | string | Task title/summary | `"Implement auth"` |
| `task.status` | enum | Current status | `backlog`, `todo`, `in_progress`, `in_review`, `blocked`, `done`, `cancelled` |
| `task.priority` | enum | Priority level | `critical`, `high`, `medium`, `low` |
| `task.assignee` | string | Assigned person/team | `"alice"` |
| `task.story_points` | int | Story point estimate | `5` |
| `task.parent_id` | string | Parent task ID (hierarchy) | `"EPIC-42"` |
| `task.blocked_by` | string | Blocking task ID | `"PROJ-100"` |
| `task.due_date` | string | Due date (ISO 8601) | `"2024-02-15"` |
| `task.url` | string | Link to external system | `"https://jira.example.com/PROJ-123"` |

#### `sprint.*` Namespace

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `sprint.id` | string | Sprint identifier | `"sprint-3"` |
| `sprint.name` | string | Sprint name | `"Sprint 3"` |
| `sprint.goal` | string | Sprint objective | `"Complete auth flow"` |
| `sprint.start_date` | string | Start date (ISO 8601) | `"2024-01-15"` |
| `sprint.end_date` | string | End date (ISO 8601) | `"2024-01-29"` |
| `sprint.planned_points` | int | Planned story points | `34` |
| `sprint.completed_points` | int | Completed story points | `28` |

### Span Event Conventions

Task lifecycle captured as span events:

| Event Name | Description | Attributes |
|------------|-------------|------------|
| `task.created` | Task created | `task.title`, `task.type` |
| `task.status_changed` | Status transition | `from`, `to` |
| `task.blocked` | Task blocked | `reason`, `blocker_id` |
| `task.unblocked` | Block removed | - |
| `task.assigned` | Assignee changed | `from`, `to` |
| `task.completed` | Task finished | - |

### Cardinality Considerations

**Safe for metrics labels** (low cardinality):
- `task.type`, `task.status`, `task.priority`
- `project.id` (bounded by organization size)
- `sprint.id` (bounded, rotates)

**Avoid in metrics labels** (high cardinality):
- `task.id`, `task.title`, `task.assignee`
- `task.url`, `task.blocked_by`

These high-cardinality attributes are appropriate for:
- Span attributes (searchable via TraceQL)
- Log attributes (indexed in Loki)
- Alert annotations (contextual)

### Relationship to Existing Conventions

| Existing Convention | Relationship |
|---------------------|--------------|
| `service.*` | `project.id` can annotate services for correlation |
| `k8s.*` | `project.id` in namespace labels, propagated to telemetry |
| `cicd.*` | `task.id` links pipelines to project tasks |

### Implementation Notes

**Tasks as Spans Pattern**:
```python
# Task lifecycle as span
tracer.start_span(
    name="task.lifecycle",
    attributes={
        "task.id": "PROJ-123",
        "task.type": "story",
        "task.status": "backlog",
        "project.id": "my-project"
    }
)
# Status change as event
span.add_event("task.status_changed", {"from": "backlog", "to": "in_progress"})
# Completion ends span
span.end()
```

**TraceQL Queries**:
```traceql
# All blocked stories
{ task.status = "blocked" && task.type = "story" }

# Tasks in a sprint
{ sprint.id = "sprint-3" }

# High-priority unfinished tasks
{ task.priority = "critical" && task.status != "done" }
```

### Prior Art

- Jira, GitHub Projects, Linear — All use similar concepts
- Grafana Incident — Models incidents with similar lifecycle patterns
- DORA Metrics — Uses similar deployment/change tracking concepts

### Reference Implementation

[ContextCore](https://github.com/contextcore/contextcore) provides a Python SDK implementing these conventions:
- `TaskTracker` class for span emission
- Dashboard templates using these attributes
- Integration examples for Jira/GitHub

---

### Checklist

- [ ] Follows [attribute naming guidelines](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/attribute-naming.md)
- [ ] Enum values use lowercase with underscores
- [ ] Cardinality documented for metrics safety
- [ ] Examples provided for each attribute
- [ ] Relationship to existing conventions documented

---

/cc @open-telemetry/semconv-approvers
