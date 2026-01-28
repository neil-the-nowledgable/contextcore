# Capability Index: Resume Guide

**Last session**: 2026-01-28
**Status**: Ready for index creation (pending final approval)

---

## Quick Context

You're creating a **capability index** for ContextCore—a queryable reference of what the SDK can do, for agents and developers.

**Core documents**:
| Document | Purpose | Location |
|----------|---------|----------|
| Preparation guide | Checklists, evidence, prompts | `inbox/CAPABILITY_INDEX_PREPARATION.md` |
| Maturity model | OTel-aligned stability definitions | `inbox/OTEL_ALIGNED_MATURITY_MODEL.md` |
| Feedback (historical) | Critical review that shaped updates | `inbox/CAPABILITY_INDEX_PREPARATION_FEEDBACK.md` |

---

## Current State

### Completed
- [x] Evidence paths verified (10+ files confirmed)
- [x] Capability discovery checkboxes filled (35+/45)
- [x] Pivoted work documented (4 items: AST merge, Hermes→Rabbit, Workflow move, Dual-emit)
- [x] Maturity criteria defined and aligned to OTel spec
- [x] Terminology mapped (draft→Development, beta→Experimental, stable→Stable)
- [x] Risk flags defined (qualitative, not numeric)
- [x] Audience prioritized (agent-first)

### Not Yet Done
- [ ] Final approval checkbox in Phase 8
- [ ] Create `contextcore.agent.yaml` (first index)
- [ ] Validate index against actual code

---

## How to Proceed

### Option A: Create the Index Now (Recommended)

The preparation is sufficient. Proceed to index creation:

1. **Check the final box** in `CAPABILITY_INDEX_PREPARATION.md` Phase 8:
   ```
   [x] Ready to proceed to index creation
   ```

2. **Use the Phase 9 prompt** from that document to create `contextcore.agent.yaml`

3. **Validate the output** by checking:
   - Do evidence paths still exist?
   - Are maturity levels accurate?
   - Are TraceQL examples runnable?

4. **Place the index** in a sensible location (suggestion: `docs/capability-index/contextcore.agent.yaml`)

### Option B: Verify Evidence First

If you want extra confidence before creating the index:

```bash
# Verify key files exist
ls -la src/contextcore/agent/insights.py
ls -la src/contextcore/agent/handoff.py
ls -la src/contextcore/agent/guidance.py
ls -la src/contextcore/agent/code_generation.py
ls -la src/contextcore/agent/size_estimation.py
```

Then proceed to Option A.

### Option C: Fill Remaining Checkboxes

If you want 100% coverage before proceeding, these checkboxes need verification:

From Phase 3:
- `[ ] Cancel task` — Check if tracker.py supports cancellation
- `[ ] * → cancelled` — Check if cancelled is a valid status
- `[ ] Blockers by status` — Check InsightQuerier filter options
- `[ ] Completion acknowledgment` — Check handoff.py for ack pattern
- `[ ] Answer questions` — Check guidance.py for question answering
- `[ ] Acknowledge constraints` — Check guidance.py for constraint ack
- `[ ] Metrics to Mimir` — Confirm if metrics are derived-only or direct

Then proceed to Option A.

---

## The Prompt to Use

When ready, use this prompt (from `CAPABILITY_INDEX_PREPARATION.md` Phase 9):

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

EVIDENCE LOCATIONS (Verified):
- /src/contextcore/agent/insights.py
- /src/contextcore/agent/handoff.py
- /src/contextcore/agent/guidance.py
- /src/contextcore/agent/code_generation.py
- /src/contextcore/agent/size_estimation.py
- /src/contextcore/agent/parts.py

Please create contextcore.agent.yaml with:
- Multi-audience descriptions (agent: terse with schemas, human: detailed)
- Evidence linked to verified paths
- Risk flags instead of confidence adjustments
- TraceQL query examples in agent descriptions
```

---

## After Creating the First Index

Follow the incremental approach from the preparation guide:

| Week | Index | Scope |
|------|-------|-------|
| 1 | `contextcore.agent.yaml` | Agent-focused (~10 capabilities) |
| 2 | `contextcore.core.yaml` | Task, sprint, metrics (~15 capabilities) |
| 3 | `contextcore.cli.yaml` | CLI commands (~20 capabilities) |
| 4 | `contextcore.packs.yaml` | Expansion packs (~10 capabilities) |

Each index is independently usable. Don't try to do all at once.

---

## Key Decisions Already Made

| Decision | Rationale |
|----------|-----------|
| Agent-first audience | Most constrained, testable, immediate value |
| OTel-aligned maturity | Industry standard, clear guarantees |
| Qualitative risk flags | Avoid arbitrary numeric adjustments |
| 80% accuracy threshold | Ship something useful over perfect preparation |
| Incremental indexes | Each usable independently, validate as you go |

---

## If You Get Stuck

1. **Re-read the preparation guide** — `inbox/CAPABILITY_INDEX_PREPARATION.md`
2. **Check the maturity model** — `inbox/OTEL_ALIGNED_MATURITY_MODEL.md`
3. **Review the original feedback** — `inbox/CAPABILITY_INDEX_PREPARATION_FEEDBACK.md`
4. **Look at the evidence** — Read the actual source files to confirm capabilities

---

## Files in This Work Stream

```
inbox/
├── CAPABILITY_INDEX_PREPARATION.md      # Main preparation guide (ready)
├── CAPABILITY_INDEX_PREPARATION_FEEDBACK.md  # Critical feedback (historical)
├── OTEL_ALIGNED_MATURITY_MODEL.md       # Maturity definitions (ready)
└── CAPABILITY_INDEX_RESUME_GUIDE.md     # This file

docs/capability-index/                    # Suggested output location
└── contextcore.agent.yaml               # First index to create
```

---

## TL;DR

1. Check the final approval box in `CAPABILITY_INDEX_PREPARATION.md`
2. Use the Phase 9 prompt to create `contextcore.agent.yaml`
3. Validate output against actual code
4. Repeat for core, cli, and packs indexes
