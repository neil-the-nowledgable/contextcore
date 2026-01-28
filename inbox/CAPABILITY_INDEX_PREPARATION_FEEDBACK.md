# Critical Feedback: Capability Index Preparation

**Document Reviewed**: `inbox/CAPABILITY_INDEX_PREPARATION.md`
**Reviewer**: Claude (Opus 4.5)
**Date**: 2026-01-28

---

## Executive Summary

The preparation guide is structurally sound but suffers from **planning-over-execution syndrome**. It creates a 9-phase process for something that could be validated incrementally. The biggest risk: this becomes a document about documents, never producing the actual capability index.

---

## Critical Issues

### 1. Unverified Evidence Claims

The document lists file paths as evidence without validation. Several are likely incorrect or outdated:

| Claimed Path | Concern |
|--------------|---------|
| `/src/contextcore/cli/sprint.py` | Sprint CLI may not exist as separate module |
| `/src/contextcore/cli/insight.py` | Insight CLI existence unverified |
| `/src/contextcore/agent/a2a_*.py` | Glob pattern—how many files? Which ones? |
| `/src/contextcore/agent/code_generation.py` | May not exist yet (recent design) |
| `/src/contextcore/contracts/` | Directory existence unverified |

**Recommendation**: Run a validation pass before proceeding. A capability index with dead links undermines trust.

### 2. Maturity Inflation

Some capabilities marked "stable" lack evidence of production use:

| Capability | Claimed Maturity | Challenge |
|------------|------------------|-----------|
| Sprint tracking | `stable` | Where is production evidence? |
| CLI (25 commands) | `stable` | Count unverified; likely fewer |
| Rabbit (alerts) | `stable` | Is this actually in production? |
| Dashboard provisioning | `stable` | 11 dashboards claimed—are all working? |

**Recommendation**: Define "stable" criteria explicitly (tests passing, docs complete, production deployment, user feedback). Then re-assess.

### 3. Empty Checklists Are a Smell

Phase 3 has ~45 checkbox items, all unchecked. This suggests:
- The document was written aspirationally, not empirically
- No one has actually walked through capability discovery
- The checkboxes may not reflect what actually exists

**Recommendation**: Fill in 5-10 checkboxes *before* calling preparation complete. Partial validation > zero validation.

### 4. Pivoted Work Section Is Critical But Empty

Phase 6 asks for pivoted/abandoned work but provides blank templates:

```
1. Original: _________________________________
   What happened: ____________________________
   Lesson: __________________________________
```

This is the most valuable section for preventing re-attempts of failed approaches. Leaving it blank means:
- Future agents will repeat mistakes
- The index won't capture institutional knowledge
- Decision archaeology becomes impossible

**Known pivoted work from project context**:
- Text-based `merge_files_intelligently()` → AST-based merge (P1 risk)
- Workflow dashboard in Rabbit → Moved to Core (design boundary fix)
- Hermes naming → Rabbit (Waabooz) naming convention change

**Recommendation**: Fill this section from `.contextcore.yaml` risks and git history before proceeding.

### 5. Confidence Score Adjustments Are Arbitrary

The document proposes risk-based confidence adjustments:

| Risk | Adjustment |
|------|------------|
| OTLP exporter failure | -0.1 |
| K8s controller restart | -0.15 |
| Portfolio needs dual-emit | -0.1 |

Where do these numbers come from? Without methodology, they're meaningless.

**Recommendation**: Either:
- Define a scoring rubric (e.g., "no retry logic = -0.1, no fallback = -0.2")
- Or remove quantitative adjustments and use qualitative flags ("risk: no retry logic")

### 6. Audience Prioritization Missing

The document identifies 5+ audiences but doesn't prioritize:

| Audience | Urgency | Index Needs |
|----------|---------|-------------|
| AI Agents using ContextCore | HIGH | Schemas, TraceQL, terse descriptions |
| Developers integrating | HIGH | API reference, examples |
| Platform engineers | MEDIUM | CRD specs, K8s configs |
| Project managers | LOW | Dashboard explanations |
| Executives | LOW | Business value metrics |

Creating one index for all audiences creates a bloated artifact no one uses well.

**Recommendation**: Create the agent-focused index FIRST (contextcore.agent.yaml). It's the most constrained, testable, and immediately useful.

### 7. Phase 9 Prompt Is Premature

The document provides a "ready to use" prompt for index creation, but:
- Evidence hasn't been verified
- Checklists haven't been filled
- Maturity hasn't been validated
- Pivoted work hasn't been captured

Using the prompt now would produce a capability index based on assumptions, not evidence.

**Recommendation**: Gate Phase 9 behind Phase 8 checklist completion. Don't skip to the prompt.

---

## Structural Observations

### What Works Well

1. **Domain organization** - The `contextcore.{module}.{capability}` naming is clean and matches code structure
2. **Expansion pack coverage** - All 6 packs identified with animal names and purposes
3. **Risk integration** - Connecting `.contextcore.yaml` risks to capability confidence is smart
4. **Multi-audience awareness** - Recognizing agents vs humans vs GTM need different descriptions

### What Needs Work

1. **No incremental validation** - The 9 phases assume waterfall execution; capability discovery should be iterative
2. **No ownership** - Who fills in each section? When?
3. **No exit criteria** - When is "preparation" done? What's the minimum viable preparation?
4. **Reference to external file** - Points to `/Users/neilyashinsky/Documents/craft/capability-index/PREPARATION.md` which may not exist or be accessible

---

## Recommended Next Steps

### Immediate (Before Index Creation)

1. **Verify top 10 evidence paths** - Confirm files exist
2. **Fill 10 Phase 3 checkboxes** - Empirical validation
3. **Document 3 pivoted approaches** - Capture from git/risks
4. **Define "stable" criteria** - What proves production readiness?

### Short-term (During Index Creation)

5. **Create agent-focused index first** - `contextcore.agent.yaml`
6. **Validate against TraceQL** - Can queries actually run?
7. **Link to working examples** - Not just paths, but runnable code

### Medium-term (After Initial Index)

8. **Add human-readable layer** - Expand terse agent descriptions
9. **Create GTM summary** - Extract business value bullets
10. **Automate evidence validation** - CI check that linked files exist

---

## Summary Table

| Aspect | Assessment | Action |
|--------|------------|--------|
| Structure | Good | Keep 9-phase organization |
| Evidence | Unverified | Validate before proceeding |
| Maturity claims | Inflated | Define criteria, re-assess |
| Checklists | Empty | Fill 10+ before Phase 9 |
| Pivoted work | Missing | Critical to capture |
| Confidence scores | Arbitrary | Define rubric or remove |
| Audience priority | Unclear | Agent-first approach |
| Exit criteria | None | Define minimum viable prep |

---

## Bottom Line

The document is a thorough template but treats preparation as an end in itself. **The goal is a capability index, not a perfect preparation document.**

Recommendation: Spend 2 hours validating evidence and filling checklists, then proceed to index creation with acknowledged gaps. An 80% accurate index that exists beats a 100% accurate preparation document that never ships.

---

*Feedback generated from document review. No codebase validation performed yet—recommend running evidence verification as next step.*
