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

- **Proposer**: Neil Yashinsky
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

### Discussion Questions

1. Does this category fit within the OTel Blueprints scope?
2. Should `project.*` and `task.*` namespaces be proposed to SemConv SIG?
3. Which existing SIGs should be involved (End-User, DevEx, CI/CD)?
4. Are there existing efforts we should coordinate with?

---

/cc @open-telemetry/governance-committee @open-telemetry/end-user-sig
