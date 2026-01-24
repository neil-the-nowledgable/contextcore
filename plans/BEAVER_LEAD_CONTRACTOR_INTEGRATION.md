# Beaver (startd8) Lead Contractor Integration Plan

**Project ID**: `beaver-lead-contractor`
**Epic**: `CONTEXTCORE-BEAVER`
**Created**: 2026-01-24
**Status**: Planning

---

## Overview

Integrate the startd8 SDK (ContextCore Beaver) Lead Contractor workflow with ContextCore task tracking to enable:

1. **Workflow execution via dashboard** - Trigger Lead Contractor from Workflow Manager
2. **Real-time task tracking** - Task status updates as spans in Tempo
3. **Decision insights** - Emit spec creation and review decisions
4. **Cost tracking** - LLM usage metrics per workflow execution

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ContextCore Workflow Manager                       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │ Projects Panel  │  │   Tasks Panel    │  │ Trigger Workflow   │  │
│  │ (Rabbit API)    │  │ (Rabbit API)     │  │ (Beaver API)       │  │
│  └────────┬────────┘  └────────┬─────────┘  └─────────┬──────────┘  │
└───────────┼────────────────────┼──────────────────────┼─────────────┘
            │                    │                      │
            ▼                    ▼                      ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        ContextCore Rabbit API                          │
│                       (localhost:8085)                                  │
│  GET /api/projects    GET /api/projects/{id}/tasks    POST /api/run   │
└───────────────────────────────────────────────────────────────────────┘
            │                    │                      │
            ▼                    ▼                      ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        startd8 SDK (Beaver)                            │
│                                                                        │
│  LeadContractorContextCoreWorkflow                                    │
│  ├── Claude Sonnet (Lead Contractor)                                  │
│  │   ├── Creates spec                                                 │
│  │   ├── Reviews drafts                                               │
│  │   └── Integrates final implementation                              │
│  └── GPT-4o-mini (Drafter)                                            │
│      └── Implements from spec                                          │
└───────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        ContextCore TaskTracker                         │
│                                                                        │
│  task.start() → status: pending                                       │
│  task.update_status("in_progress")                                    │
│  task.add_event("spec_created", {...})                                │
│  task.add_event("draft_1_created", {...})                             │
│  task.add_event("review_1_complete", {score: 85})                     │
│  task.complete() → status: completed                                  │
└───────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        Tempo (Trace Backend)                           │
│  TraceQL: { project.id = "beaver-lead-contractor" }                   │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Tasks

### Phase 1: API Integration

| Task ID | Title | Type | Status | Description |
|---------|-------|------|--------|-------------|
| BLC-001 | Add workflow run endpoint to Rabbit API | task | pending | POST /api/run to trigger Lead Contractor workflow |
| BLC-002 | Implement workflow status endpoint | task | pending | GET /api/workflows/{id}/status for real-time updates |
| BLC-003 | Add workflow history endpoint | task | pending | GET /api/workflows for completed workflow runs |

### Phase 2: Dashboard Integration

| Task ID | Title | Type | Status | Description |
|---------|-------|------|--------|-------------|
| BLC-004 | Update Workflow Manager trigger panel | task | pending | Configure button to call POST /api/run |
| BLC-005 | Add workflow status panel | task | pending | Show active workflow progress |
| BLC-006 | Add workflow history panel | task | pending | Display completed workflow runs with costs |

### Phase 3: Task Tracking

| Task ID | Title | Type | Status | Description |
|---------|-------|------|--------|-------------|
| BLC-007 | Test ContextCore task tracking | task | pending | Verify tasks appear in Tempo as spans |
| BLC-008 | Add insight emission | task | pending | Emit decisions for spec and review phases |
| BLC-009 | Add cost tracking metrics | task | pending | Emit LLM cost as span attributes |

### Phase 4: Documentation

| Task ID | Title | Type | Status | Description |
|---------|-------|------|--------|-------------|
| BLC-010 | Update CLAUDE.md with Beaver integration | task | pending | Document workflow usage in project context |
| BLC-011 | Create workflow usage guide | task | pending | End-to-end guide for running Lead Contractor |

---

## Configuration

### Environment Variables

```bash
# startd8 SDK
export ANTHROPIC_API_KEY="sk-..."
export OPENAI_API_KEY="sk-..."

# ContextCore
export OTEL_EXPORTER_OTLP_ENDPOINT="localhost:4318"  # K8s Tempo
export CONTEXTCORE_PROJECT_ID="beaver-lead-contractor"
```

### Workflow Config

```json
{
  "task_description": "Implement feature X",
  "task_id": "BLC-XXX",
  "project_id": "beaver-lead-contractor",
  "drafter_agent": "openai:gpt-4o-mini",
  "emit_insights": true
}
```

---

## Success Criteria

1. [ ] Can trigger Lead Contractor from Workflow Manager dashboard
2. [ ] Task status updates visible in ContextCore: Project Progress dashboard
3. [ ] Workflow decisions emit as insights queryable in Tempo
4. [ ] Cost per workflow run tracked and visible
5. [ ] End-to-end workflow completes with task marked as done

---

## Dependencies

- **ContextCore Rabbit** (Waabooz) - API server for projects/tasks
- **ContextCore Fox** (Waagosh) - Grafana dashboards
- **ContextCore Beaver** (Amik) - startd8 SDK with Lead Contractor workflow
- **K8s Observability Stack** - Tempo for trace storage

---

## Next Steps

1. Create project in ContextCore: `contextcore project create beaver-lead-contractor`
2. Import tasks from this plan
3. Start work from Workflow Manager dashboard

---

*Generated by Claude for ContextCore workflow tracking*
