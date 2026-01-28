# ContextCore Capability Index Preparation

A guide to preparing for capability indexing of the ContextCore SDK and ecosystem.

---

## Project Context

**What ContextCore Is**: A unified project management observability framework that models tasks as OpenTelemetry spans, enabling humans and AI agents to share a common knowledge repository.

**Core Insight**: Tasks ARE Spans—same lifecycle (start → progress → end), same attributes, same queryability.

**Why Index Capabilities**: To create a canonical, queryable reference for:
- Agents discovering what ContextCore can do
- Humans understanding available features
- GTM teams positioning capabilities
- Future gap detection between intent and implementation

---

## Critical: Read Before Proceeding

> **The goal is a capability index, not a perfect preparation document.**
>
> Spend time validating evidence and filling checklists, then proceed to index creation with acknowledged gaps. An 80% accurate index that exists beats a 100% accurate preparation document that never ships.

### Minimum Viable Preparation

Before creating the index, complete at minimum:
- [ ] Verify 10 evidence paths (files exist)
- [ ] Fill 10 capability discovery checkboxes
- [ ] Document 3 pivoted/abandoned approaches
- [ ] Define what "stable" means for this project

---

## Phase 1: Audience Prioritization

**Create the agent-focused index FIRST.** It's the most constrained, testable, and immediately useful.

### Priority Order

| Priority | Audience | Rationale |
|----------|----------|-----------|
| **1 (NOW)** | AI Agents using ContextCore | Most constrained (schemas required), testable, immediate value |
| **2 (NOW)** | Developers integrating | High urgency, needs API reference |
| **3 (LATER)** | Platform engineers | Medium urgency, K8s/CRD focus |
| **4 (LATER)** | Project managers | Lower urgency, dashboard consumers |
| **5 (LATER)** | Executives | Lowest urgency, derived from above |

### First Index Target

Create `contextcore.agent.yaml` covering:
- Insight emission and querying
- Handoff protocols
- Guidance constraint reading
- TraceQL patterns for agents

This scopes the initial effort and produces something usable immediately.

---

## Phase 2: Capability Domains (Verified)

Evidence paths verified 2026-01-28.

### Core SDK (`contextcore.*`)

| Subdomain | Evidence Location | Verified |
|-----------|-------------------|----------|
| `contextcore.task` | `/src/contextcore/tracker.py` | ✓ |
| `contextcore.sprint` | `/src/contextcore/tracker.py` | ✓ |
| `contextcore.insight` | `/src/contextcore/agent/insights.py` | ✓ |
| `contextcore.handoff` | `/src/contextcore/agent/handoff.py` | ✓ |
| `contextcore.guidance` | `/src/contextcore/agent/guidance.py` | ✓ |
| `contextcore.logger` | `/src/contextcore/logger.py` | ✓ |
| `contextcore.metrics` | `/src/contextcore/metrics.py` | ✓ |
| `contextcore.state` | `/src/contextcore/state.py` | ✓ |
| `contextcore.crd` | `/src/contextcore/models.py`, `/crds/` | ✓ |
| `contextcore.detector` | `/src/contextcore/detector.py` | ✓ |

### Agent Communication (`contextcore.agent.*`)

| Subdomain | Evidence Location | Verified |
|-----------|-------------------|----------|
| `contextcore.agent.insight` | `/src/contextcore/agent/insights.py` | ✓ |
| `contextcore.agent.handoff` | `/src/contextcore/agent/handoff.py` | ✓ |
| `contextcore.agent.guidance` | `/src/contextcore/agent/guidance.py` | ✓ |
| `contextcore.agent.a2a` | 5 files: `a2a_adapter.py`, `a2a_client.py`, `a2a_server.py`, `a2a_messagehandler.py`, `a2a_package.py` | ✓ |
| `contextcore.agent.code_generation` | `/src/contextcore/agent/code_generation.py` | ✓ |
| `contextcore.agent.size_estimation` | `/src/contextcore/agent/size_estimation.py` | ✓ |
| `contextcore.agent.parts` | `/src/contextcore/agent/parts.py` (AST merge) | ✓ |

### CLI (`contextcore.cli.*`) — 20 Command Modules

| Command | Evidence Location | Verified |
|---------|-------------------|----------|
| `contextcore task` | `/src/contextcore/cli/task.py` | ✓ |
| `contextcore sprint` | `/src/contextcore/cli/sprint.py` | ✓ |
| `contextcore insight` | `/src/contextcore/cli/insight.py` | ✓ |
| `contextcore install` | `/src/contextcore/cli/install.py` | ✓ |
| `contextcore dashboards` | `/src/contextcore/cli/dashboards.py` | ✓ |
| `contextcore demo` | `/src/contextcore/cli/demo.py` | ✓ |
| `contextcore metrics` | `/src/contextcore/cli/metrics.py` | ✓ |
| `contextcore skill` | `/src/contextcore/cli/skill.py` | ✓ |
| `contextcore knowledge` | `/src/contextcore/cli/knowledge.py` | ✓ |
| `contextcore graph` | `/src/contextcore/cli/graph.py` | ✓ |
| `contextcore ops` | `/src/contextcore/cli/ops.py` | ✓ |
| `contextcore git` | `/src/contextcore/cli/git.py` | ✓ |
| `contextcore review` | `/src/contextcore/cli/review.py` | ✓ |
| `contextcore contract` | `/src/contextcore/cli/contract.py` | ✓ |
| `contextcore slo_tests` | `/src/contextcore/cli/slo_tests.py` | ✓ |
| `contextcore rbac` | `/src/contextcore/cli/rbac.py` | ✓ |
| `contextcore value` | `/src/contextcore/cli/value.py` | ✓ |
| `contextcore sync` | `/src/contextcore/cli/sync.py` | ✓ |
| `contextcore tui` | `/src/contextcore/cli/tui.py` | ✓ |
| `contextcore core` | `/src/contextcore/cli/core.py` | ✓ |

### Contracts (`contextcore.contracts.*`) — 6 Modules

| Module | Evidence Location | Verified |
|--------|-------------------|----------|
| Types | `/src/contextcore/contracts/types.py` | ✓ |
| Metrics | `/src/contextcore/contracts/metrics.py` | ✓ |
| Validators | `/src/contextcore/contracts/validators.py` | ✓ |
| Validate | `/src/contextcore/contracts/validate.py` | ✓ |
| Queries | `/src/contextcore/contracts/queries.py` | ✓ |
| Timeouts | `/src/contextcore/contracts/timeouts.py` | ✓ |

### Expansion Packs

| Pack | Animal | Evidence Location | Verified |
|------|--------|-------------------|----------|
| **Rabbit** | Waabooz | `/contextcore-rabbit/` | Needs verification |
| **Beaver** | Amik | `/contextcore-beaver/` | Needs verification |
| **Squirrel** | Ajidamoo | `/contextcore-squirrel/` | Needs verification |
| **Fox** | Waagosh | Design docs only | Not implemented |
| **Coyote** | Wiisagi-ma'iingan | Design docs only | Not implemented |
| **Owl** | Gookooko'oo | `/contextcore-owl/` | Internal only |

---

## Phase 3: Capability Discovery (Partial Validation)

Work through these questions. **Fill at least 10 before proceeding to index creation.**

### Task Tracking Capabilities

```
1. What task operations are supported?
   [✓] Create task (start span)
   [✓] Update status
   [✓] Block/unblock
   [✓] Complete task (end span)
   [✓] Cancel task (tracker.py:648)
   [✓] Link parent/child
   [✓] Add story points
   [✓] Assign/reassign

2. What task types exist?
   [✓] Epic
   [✓] Story
   [✓] Task
   [✓] Subtask
   [✓] Bug
   [✓] Spike
   [✓] Incident

3. What status transitions are tracked?
   [✓] backlog → todo
   [✓] todo → in_progress
   [✓] in_progress → in_review
   [✓] in_review → done
   [✓] * → blocked
   [✓] * → cancelled (types.py:31 TaskStatus.CANCELLED)
```

### Agent Communication Capabilities

```
4. What can agents emit?
   [✓] Decisions (with confidence)
   [✓] Recommendations
   [✓] Blockers
   [✓] Discoveries
   [✓] Lessons learned
   [✓] Questions for humans
   [✓] Risks
   [✓] Progress updates

5. What can agents query?
   [✓] Prior decisions by project
   [✓] Lessons by category
   [✓] Blockers by status (insights.py:878 get_blockers())
   [✓] Insights by confidence threshold
   [✓] Insights by time range
   [✓] Insights by file path (applies_to)

6. What handoff capabilities exist?
   [✓] Initiate handoff
   [✓] Accept/reject handoff
   [✓] Track handoff status
   [✓] Size estimation (tokens, lines)
   [✓] Decomposition negotiation
   [✓] Completion acknowledgment (handoff.py:60 HandoffStatus.COMPLETED)

7. What guidance capabilities exist?
   [✓] Read constraints
   [✓] Check constraints for path
   [✓] Read open questions
   [✓] Answer questions (guidance.py:365 GuidanceResponder.answer_question())
   [✓] Acknowledge constraints (guidance.py:112 get_constraints_for_path())
```

### Observability Capabilities

```
8. What telemetry is emitted?
   [✓] Spans to Tempo (tasks, insights, handoffs)
   [✓] Logs to Loki (status changes, events)
   [✓] Metrics to Mimir — derived only (spans → Tempo → Mimir queries)
```

**Checkboxes filled: 35+ / 45** — Sufficient for initial index creation.

---

## Phase 4: Maturity Criteria (Defined)

> **Reference**: See `inbox/OTEL_ALIGNED_MATURITY_MODEL.md` for full OTel-aligned maturity definitions.

### Terminology Mapping

| This Document | OTel-Aligned | Meaning |
|---------------|--------------|---------|
| `draft` | Development | Incomplete, untested, may be removed |
| `beta` | Experimental | Works, but API may change with notice |
| `stable` | Stable | Production-ready, backward-compatible |

### What "Stable" Means for ContextCore

A capability is `stable` (OTel: Stable) if ALL of the following are true:

| Criterion | Evidence Required |
|-----------|-------------------|
| **Code complete** | Implementation covers documented behavior |
| **Tests pass** | Unit tests exist and pass |
| **Documentation exists** | API reference or docstrings |
| **Example exists** | In `/examples/` or inline |
| **Production validation** | Demo generator exercises it OR external use |

A capability is `beta` (OTel: Experimental) if:
- Code exists and works
- May lack tests, docs, or production validation
- API may change with 30-day notice

A capability is `draft` (OTel: Development) if:
- Design exists but implementation incomplete
- Or exists but untested/undocumented
- May be removed without notice

### Maturity Assessment (Re-evaluated)

| Capability Area | Previous | Revised | OTel Level | Rationale |
|-----------------|----------|---------|------------|-----------|
| Task tracking | stable | **stable** | Stable | Code, tests, examples, demo generator |
| Sprint tracking | stable | **beta** | Experimental | Code exists, limited testing evidence |
| Insight emission | stable | **stable** | Stable | Code, tests, examples |
| Insight querying | beta | **stable** | Stable | Code, tests, examples, demo generator |
| Handoff system | beta | **beta** | Experimental | Implemented, tests exist |
| Generation contracts | beta | **beta** | Experimental | Recent implementation, P1 risk mitigated |
| Guidance system | beta | **beta** | Experimental | Implemented, limited docs |
| OTel GenAI dual-emit | beta | **beta** | Experimental | Migration in progress |
| CLI (20 commands) | stable | **beta** | Experimental | Many commands, varying test coverage |
| Dashboard provisioning | stable | **beta** | Experimental | Dashboards exist, full coverage unverified |
| Rabbit (alerts) | stable | **beta** | Experimental | Needs production evidence |
| Beaver (LLM) | beta | **beta** | Experimental | StartD8 integration |
| Coyote (orchestration) | draft | **draft** | Development | Design phase only |
| Squirrel (skills) | beta | **beta** | Experimental | Skills browser works |
| Fox (enrichment) | — | **draft** | Development | Design only |

---

## Phase 5: Pivoted/Abandoned Work (Critical)

**This section prevents future agents from repeating mistakes.**

### 1. Text-Based File Merge → AST-Based Merge

```
Original Intent: merge_files_intelligently() using text-based diff/patch
What Happened: Corrupted Python files when merging class definitions
Status: RESOLVED (2026-01-26)
Solution: Rewrote using Python AST for structure-aware merging
Lesson: Text-based merging is insufficient for code; always use language-aware tools
Evidence: /src/contextcore/agent/parts.py, test_ast_merge.py (42 regression tests)
```

### 2. Hermes Naming → Rabbit (Waabooz)

```
Original Intent: Name alert automation component "Hermes" (Greek messenger god)
What Happened: Decided to use Anishinaabe (Ojibwe) naming to honor indigenous peoples
Status: RENAMED
Solution: All expansion packs use animal names with Anishinaabe translations
Lesson: Naming conventions should reflect project values; consistency matters
Evidence: docs/NAMING_CONVENTION.md
```

### 3. Workflow Dashboard in Rabbit → Moved to Core

```
Original Intent: Workflow triggering dashboard as part of Rabbit (alert automation)
What Happened: Violated design principle "Rabbit is for triggering, NOT orchestrating"
Status: MOVED
Solution: Workflow dashboard is now part of Core dashboards, Rabbit remains fire-and-forget
Lesson: Respect component boundaries; if it doesn't fit, it belongs elsewhere
Evidence: contextcore-rabbit/README.md design principles
```

### 4. Single-Emit Tempo → Dual-Emit Tempo + Loki

```
Original Intent: Emit task data to Tempo only (spans are sufficient)
What Happened: Portfolio dashboard couldn't derive metrics from spans alone
Status: EVOLVED
Solution: Dual-emit to both Tempo (hierarchy, timing) and Loki (events, metrics derivation)
Lesson: Different backends excel at different queries; don't force one to do everything
Evidence: CONTEXTCORE_OTEL_MODE env var, demo/exporter.py
```

---

## Phase 6: Risk-Based Confidence (Qualitative)

Instead of arbitrary numeric adjustments, use qualitative flags:

| Capability | Risk Flag | Impact |
|------------|-----------|--------|
| All emission capabilities | `risk:no-retry-on-export-failure` | May lose telemetry silently |
| State persistence | `risk:k8s-restart-loses-in-flight` | Spans may be incomplete |
| Portfolio dashboard | `risk:requires-dual-emit` | Won't work with Tempo-only setup |
| Task completion | `risk:execution-not-value` | "Done" means code done, not value delivered |

These flags appear in capability entries rather than adjusting a numeric score.

---

## Phase 7: Naming Convention

Follow this naming pattern aligned with existing code structure:

```
contextcore.{module}.{capability}

Examples:
contextcore.task.create
contextcore.task.update_status
contextcore.insight.emit_decision
contextcore.insight.query_lessons
contextcore.handoff.initiate
contextcore.guidance.read_constraints
contextcore.cli.task_start
contextcore.dashboard.provision
```

### Expansion Pack Naming

```
contextcore.{pack}.{capability}

Examples:
contextcore.rabbit.trigger_action
contextcore.rabbit.webhook_grafana
contextcore.beaver.llm_request
contextcore.squirrel.skill_query
```

### Semantic Convention Alignment

ContextCore defines semantic conventions. Capability IDs should align:

| Attribute Prefix | Capability Domain |
|------------------|-------------------|
| `task.*` | `contextcore.task.*` |
| `insight.*` | `contextcore.insight.*` |
| `agent.*` | `contextcore.agent.*` |
| `handoff.*` | `contextcore.handoff.*` |
| `project.*` | `contextcore.project.*` |

---

## Phase 8: Pre-Index Checklist

**All boxes must be checked before proceeding to Phase 9.**

### Evidence Validation (Minimum 10)

```
[✓] /src/contextcore/tracker.py exists
[✓] /src/contextcore/agent/insights.py exists
[✓] /src/contextcore/agent/handoff.py exists
[✓] /src/contextcore/agent/guidance.py exists
[✓] /src/contextcore/agent/code_generation.py exists
[✓] /src/contextcore/cli/task.py exists
[✓] /src/contextcore/cli/sprint.py exists
[✓] /src/contextcore/cli/insight.py exists
[✓] /src/contextcore/contracts/types.py exists
[✓] /src/contextcore/agent/parts.py exists (AST merge)
```

### Capability Discovery (Minimum 10 filled)

```
[✓] 35+ checkboxes filled in Phase 3
```

### Pivoted Work (Minimum 3)

```
[✓] AST merge pivot documented
[✓] Hermes → Rabbit naming documented
[✓] Workflow dashboard move documented
[✓] Dual-emit evolution documented
```

### Maturity Criteria

```
[✓] "Stable" criteria defined
[✓] All capabilities re-assessed against criteria
```

### Exit Criteria Met

```
[✓] Evidence paths verified
[✓] Checkboxes filled
[✓] Pivoted work captured
[✓] Maturity defined
[x] Ready to proceed to index creation (completed 2026-01-28)
```

---

## Phase 9: Index Creation Prompt

**GATE**: Do not use this prompt until Phase 8 checklist is complete.

---

**Prompt for ContextCore Capability Index:**

```
Create a capability index for ContextCore using the capability-index schema.

PROJECT CONTEXT:
- Name: ContextCore (Spider / Asabikeshiinh)
- Purpose: Project management as observability—tasks as OTel spans
- Primary audience: AI agents integrating ContextCore (FIRST), then developers
- Current phase: Phase 4 (OTel GenAI Alignment)

FIRST INDEX TO CREATE:
contextcore.agent.yaml — Agent-focused capabilities only

CAPABILITIES TO INCLUDE:
1. contextcore.insight.emit — Emit decisions, lessons, blockers, discoveries
2. contextcore.insight.query — Query prior insights by project, type, confidence
3. contextcore.handoff.initiate — Start agent-to-agent delegation
4. contextcore.handoff.receive — Accept and process handoffs
5. contextcore.guidance.read_constraints — Get human-defined constraints
6. contextcore.guidance.check_path — Check constraints for specific file path
7. contextcore.code_generation.contract — Define expected output size/format
8. contextcore.size_estimation.estimate — Estimate output before generation

MATURITY (Validated):
- stable: insight.emit, insight.query (code, tests, examples exist)
- beta: handoff.*, guidance.*, code_generation.*, size_estimation.*

KNOWN RISKS (as flags, not scores):
- risk:no-retry-on-export-failure
- risk:k8s-restart-loses-in-flight

PIVOTED WORK TO REFERENCE:
- AST merge replaced text merge (see parts.py)
- Dual-emit required for portfolio dashboard

EVIDENCE LOCATIONS (Verified):
- /src/contextcore/agent/insights.py
- /src/contextcore/agent/handoff.py
- /src/contextcore/agent/guidance.py
- /src/contextcore/agent/code_generation.py
- /src/contextcore/agent/size_estimation.py
- /src/contextcore/agent/parts.py

SEMANTIC CONVENTIONS:
- insight.id, insight.type, insight.confidence, insight.summary
- handoff.id, handoff.status, handoff.from_agent, handoff.to_agent
- agent.id, agent.session_id, agent.type

Please create contextcore.agent.yaml with:
- Multi-audience descriptions (agent: terse with schemas, human: detailed)
- Evidence linked to verified paths
- Risk flags instead of confidence adjustments
- TraceQL query examples in agent descriptions
```

---

## Appendix: ContextCore-Specific Patterns

### Dual-Emit Pattern

Every capability that emits telemetry should document:
- What goes to Tempo (spans)
- What goes to Loki (logs)
- Why both are needed

### Generation Contract Pattern

Code generation capabilities should document:
- `expected_output` schema (max_lines, max_tokens)
- Decomposition behavior when limits exceeded
- Completeness markers

### Guidance Pattern

Capabilities that respect human guidance should document:
- Which constraints they check
- How blocking vs advisory differs
- How questions are surfaced

---

## Appendix: Incremental Approach

Don't try to index everything at once. Follow this order:

1. **Week 1**: `contextcore.agent.yaml` (agent-focused, ~10 capabilities)
2. **Week 2**: `contextcore.core.yaml` (task, sprint, metrics, ~15 capabilities)
3. **Week 3**: `contextcore.cli.yaml` (CLI commands, ~20 capabilities)
4. **Week 4**: `contextcore.packs.yaml` (expansion packs, ~10 capabilities)

Each index is usable independently. Validate each before proceeding.

---

*This preparation guide is specific to ContextCore. For the general capability index preparation guide, see `/Users/neilyashinsky/Documents/craft/capability-index/PREPARATION.md`.*

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `inbox/OTEL_ALIGNED_MATURITY_MODEL.md` | Full OTel-aligned maturity definitions, versioning, deprecation policies |
| `docs/semantic-conventions.md` | Attribute definitions for telemetry |
| `.contextcore.yaml` | Risk definitions affecting capability confidence |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-28 | Initial creation |
| 2026-01-28 | Incorporated feedback: verified evidence, filled checkboxes, added pivoted work, defined stable criteria, added audience priority, added exit criteria, replaced numeric confidence with qualitative flags |
| 2026-01-28 | Aligned with OTEL_ALIGNED_MATURITY_MODEL.md: added terminology mapping, fixed insight.query to Stable, added Fox to registry, added Related Documents section |
