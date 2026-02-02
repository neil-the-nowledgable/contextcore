# GitHub Issue: Proposed Blueprint Category - Project Management Observability

> **Repository**: `open-telemetry/community`
> **Type**: Project Proposal
> **Status**: Draft - Ready for Submission

---

## Issue Title

```
[Project Proposal] Project Management Observability Blueprint
```

## Issue Body

### Summary

This proposal introduces a new OTel Blueprint category for **Project Management Observability** — modeling project tasks as OpenTelemetry spans to eliminate manual status reporting and enable real-time portfolio visibility.

### Problem Statement

Organizations face significant challenges connecting project management to observability:

1. **Manual Status Reporting**: Engineers spend 4-6 hours/week per team manually updating ticket status and compiling progress reports.

2. **Disconnected Project and Runtime Data**: Production incidents can't be easily traced to the project tasks that introduced them. Deployments aren't correlated with completed tasks.

3. **No Portfolio-Level Visibility**: "How many projects are blocked?" requires manual survey. No consistent health metrics across projects.

### Proposed Solution

Model project tasks as OpenTelemetry spans with standardized semantic conventions:

```yaml
# Core task attributes
task.id: "PROJ-123"
task.type: "story"           # epic | story | task | subtask | bug
task.status: "in_progress"   # backlog | todo | in_progress | blocked | done
task.parent_id: "EPIC-42"    # Hierarchy via span parent
project.id: "my-project"

# Business context
business.criticality: "critical"
business.owner: "commerce-team"
```

Key patterns:
- **Tasks as Spans**: Task lifecycle maps to span start/end, status changes as events
- **Artifact-Based Derivation**: Status derived from commits, PRs, CI results
- **TraceQL Queries**: `{ task.status = "blocked" && project.id = "X" }`

### Deliverables

1. **Blueprint Document**: Following OTel Blueprint Template (Diagnosis → Guiding Policies → Coherent Actions)
2. **Semantic Conventions**: `project.*`, `task.*`, `sprint.*` namespaces
3. **Reference Implementation**: ContextCore SDK and dashboards
4. **Implementation Guide**: Step-by-step adoption guide

### Validation

- [ ] 5+ end-user interviews conducted
- [ ] Problem validation score ≥ 3.5/5.0
- [ ] Solution fit score ≥ 3.5/5.0
- [ ] 2+ reference architecture commitments

*Validation evidence will be attached before final submission.*

### Scope

**In Scope**:
- Task lifecycle telemetry (spans, events, attributes)
- Project and sprint context attributes
- Integration patterns with issue trackers (Jira, GitHub, Linear)
- Dashboard specifications for portfolio and project views
- Value-based observability derivation (criticality → sampling)

**Out of Scope**:
- Specific issue tracker implementations (covered in integration guides)
- Real-time collaboration features
- Project planning/scheduling algorithms

### Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Format/Scope Decision | 2 weeks | Agreed blueprint structure |
| Documentation | 4 weeks | Blueprint document, semconv |
| Reference Implementation | 4 weeks | ContextCore SDK + examples |
| Community Review | 2 weeks | Feedback incorporation |

### Leadership

- **Proposer**: Force Multiplier Labs
- **Sponsorship Sought**: End-User SIG, DevEx SIG

### Related Work

- [OTel Blueprints Project](https://github.com/open-telemetry/community/blob/main/projects/otel-blueprints.md)
- [CI/CD Semantic Conventions](https://github.com/open-telemetry/semantic-conventions/tree/main/docs/cicd) (complementary)
- [ContextCore Reference Implementation](https://github.com/contextcore/contextcore)

### Success Criteria

1. Blueprint document accepted into OTel documentation
2. Semantic conventions proposed to SemConv SIG
3. 3+ organizations adopt patterns within 6 months
4. Measurable reduction in manual status reporting (target: 50%)

---

## 👥 Value by Role

This section articulates the specific value proposition for each persona who benefits from Project Management Observability.

### Software Engineer

| Aspect | Details |
|--------|---------|
| **Pain Point** | "I spend Friday afternoons updating Jira tickets instead of coding" |
| **Benefit** | Task status derived automatically from commits, PRs, and CI results |
| **Time Saved** | 4-6 hours/week eliminated manual status reporting |
| **Capability Unlocked** | Focus on building; let artifacts speak for themselves |

**Before**: Manually update ticket → Write standup notes → Copy to weekly report → Field "what's the status?" questions

**After**: Commit code → Status auto-derived → Dashboards always current → Questions answered by TraceQL

```bash
# Engineer's workflow becomes:
git commit -m "feat: implement auth flow"
# Task PROJ-123 automatically transitions to "in_progress"
# PR merge → task transitions to "done"
# No manual Jira updates required
```

---

### Engineering Manager

| Aspect | Details |
|--------|---------|
| **Pain Point** | "I don't know which projects are actually blocked until standup" |
| **Benefit** | Real-time portfolio visibility without polling team members |
| **Time Saved** | 3-4 hours/week compiling status reports |
| **Capability Unlocked** | Proactive intervention before blockers cascade |

**Key Queries**:
```
# What's blocked right now?
{ task.status = "blocked" && business.owner = "my-team" }

# What shipped this sprint?
{ task.status = "done" && sprint.id = "sprint-42" }

# Which critical tasks are at risk?
{ business.criticality = "critical" && task.status = "in_progress" }
  | where duration > 5d
```

**Dashboard Value**:
- **Portfolio Overview**: All projects, color-coded health
- **Blockers Panel**: Auto-populated, no manual triage
- **Velocity Trends**: Derived from task completion spans

---

### VP of Engineering / CTO

| Aspect | Details |
|--------|---------|
| **Pain Point** | "I need portfolio health for the board meeting but data is 2 weeks stale" |
| **Benefit** | Real-time executive dashboards derived from actual work artifacts |
| **Strategic Value** | Investment decisions based on current data, not stale reports |
| **Capability Unlocked** | Connect project execution to business outcomes |

**Executive Dashboard Panels**:

| Panel | Query | Insight |
|-------|-------|---------|
| Portfolio Health | `count_over_time({task.status="blocked"})` | Systemic blockers trend |
| Delivery Velocity | `rate({task.status="done"})` | Throughput by business unit |
| Critical Path | `{business.criticality="critical"}` | Revenue-impacting work status |
| Resource Allocation | `{task.type="story"} \| by business.owner` | Team capacity distribution |

**ROI Calculation**:
```
Engineering team: 50 engineers
Manual reporting: 5 hours/engineer/week
Annual cost: 50 × 5 × 52 × $75/hr = $975,000/year

With Project O11y:
Reporting time: ~30 min/engineer/week (review only)
Annual cost: 50 × 0.5 × 52 × $75/hr = $97,500/year

Savings: $877,500/year + improved decision quality
```

---

### SRE / Platform Engineer

| Aspect | Details |
|--------|---------|
| **Pain Point** | "Production incident, but which release introduced it? Which task?" |
| **Benefit** | Trace production issues back to originating project tasks |
| **Capability Unlocked** | Unified query across project AND runtime telemetry |

**Incident Correlation**:
```
# Find the task that introduced the failing code
{ span.kind = "server" && http.status_code >= 500 }
  | link task.id

# Query both runtime trace AND project task
{ task.id = "PROJ-456" } | select task.title, task.completed_at
{ service.name = "checkout" && deployment.task_id = "PROJ-456" }
```

**Value-Based Sampling**:
```yaml
# Automatically derived from ProjectContext CRD
business.criticality: critical → trace_sampling: 100%
business.criticality: high     → trace_sampling: 50%
business.criticality: medium   → trace_sampling: 10%
```

---

### Product Manager

| Aspect | Details |
|--------|---------|
| **Pain Point** | "Engineering says it's 80% done but I have no visibility" |
| **Benefit** | Objective progress metrics derived from artifacts, not estimates |
| **Capability Unlocked** | Data-driven roadmap decisions |

**Progress Visibility**:
```
# Epic completion status (objective, not estimated)
{ task.type = "epic" && task.id = "EPIC-42" }
  | child_count(status = "done") / child_count(*)

# Feature delivery timeline (actual, not projected)
{ task.type = "story" && feature.id = "new-checkout" }
  | histogram(duration)
```

**Stakeholder Questions Answered**:
- "When will this ship?" → Historical cycle time + current WIP
- "What got done this quarter?" → `{ task.status = "done" && completed_at > 90d }`
- "Why is this taking so long?" → `{ task.id = "X" } | events` shows blocker history

---

### Adoption Path by Role

| Role | Start Here | Quick Win | Full Value |
|------|------------|-----------|------------|
| **Engineer** | CLI task tracking | Auto-status from commits | Zero manual reporting |
| **EM** | Blockers dashboard | Sprint velocity panel | Portfolio health alerts |
| **CTO** | Executive summary dashboard | Delivery trends | Investment ROI correlation |
| **SRE** | Task-trace linking | Incident-to-task queries | Value-based sampling |
| **PM** | Progress dashboard | Epic completion metrics | Roadmap analytics |

---

### Discussion Questions

1. Does this category fit within the OTel Blueprints scope?
2. Should `project.*` and `task.*` namespaces be proposed to SemConv SIG?
3. Which existing SIGs should be involved (End-User, DevEx, CI/CD)?
4. Are there existing efforts we should coordinate with?

---

## ⚓ Harbor Tour: Local Development Infrastructure

This section provides orientation for contributors who want to explore the Project Management Observability patterns locally.

### Prerequisites

```bash
# Required
- Docker & Docker Compose
- Python 3.9+
- pip3

# Optional (for Kubernetes features)
- kind or minikube
- kubectl
- helm
```

### Quick Start: See It In Action

```bash
# 1. Clone ContextCore reference implementation
git clone https://github.com/neil-the-nowledgable/contextcore.git
cd contextcore

# 2. Start the observability stack
make full-setup    # Starts Grafana, Tempo, Loki, Mimir

# 3. Generate demo project data (3 months of task history)
contextcore demo generate --project online-boutique
contextcore demo load --file ./demo_output/demo_spans.json

# 4. Explore in Grafana
open http://localhost:3000    # admin/admin
```

### Local Observability Stack

| Service | URL | Purpose |
|---------|-----|---------|
| Grafana | http://localhost:3000 | Dashboards & visualization |
| Tempo | http://localhost:3200 | Task spans (traces) storage |
| Loki | http://localhost:3100 | Structured logs, metrics derivation |
| Mimir | http://localhost:9009 | Long-term metrics storage |

### Key Explorations

**1. Tasks as Spans (TraceQL)**
```
# Find all blocked tasks
{ task.status = "blocked" }

# Tasks by project and type
{ project.id = "online-boutique" && task.type = "story" }

# Task hierarchy (epic → story → task)
{ task.parent_id = "EPIC-42" }
```

**2. Pre-Built Dashboards**
- **Project Portfolio Overview**: Cross-project health metrics
- **Project Progress**: Task completion trends, WIP
- **Sprint Metrics**: Velocity, cycle time

**3. CLI Commands**
```bash
# Track a task
contextcore task start --id TASK-1 --title "Feature" --type story
contextcore task update --id TASK-1 --status in_progress
contextcore task complete --id TASK-1

# View project metrics
contextcore metrics summary --project my-project
```

### Project Structure (Reference Implementation)

```
contextcore/
├── src/contextcore/
│   ├── tracker.py       # TaskTracker (tasks as spans)
│   ├── logger.py        # TaskLogger (structured logs)
│   ├── metrics.py       # Derived project metrics
│   └── demo/            # Demo data generation
├── grafana/provisioning/dashboards/json/
│   └── *.json           # 6 pre-built dashboards
├── docs/
│   └── semantic-conventions.md  # Attribute reference
└── examples/
    └── 01_basic_task_tracking.py  # Runnable example
```

### Cleanup

```bash
make down      # Stop stack (preserves data)
make destroy   # Full cleanup (prompts for confirmation)
```

---

/cc @open-telemetry/governance-committee @open-telemetry/end-user-sig
