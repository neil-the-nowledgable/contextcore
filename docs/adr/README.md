# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the Wayfinder ecosystem.

## What is an ADR?

An ADR captures a significant technical or design decision:
- **What** was decided
- **Why** it was decided (context, constraints, alternatives)
- **Consequences** (tradeoffs, what changes as a result)

ADRs prevent re-litigation of past decisions and help new team members understand the reasoning behind the architecture.

---

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-tasks-as-spans.md) | Model Tasks as OpenTelemetry Spans | Accepted | 2026-01-01 |
| [002](002-naming-wayfinder.md) | Naming Convention — Wayfinder and ContextCore | Accepted | 2026-01-28 |

---

## Status Definitions

| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion, not yet decided |
| **Accepted** | Decision made and in effect |
| **Deprecated** | Decision superseded by a newer ADR |
| **Superseded** | Replaced by another ADR (link to replacement) |

---

## Template

```markdown
# ADR-NNN: [Title]

**Status:** Proposed / Accepted / Deprecated
**Date:** YYYY-MM-DD
**Author:** [Name]

## Context

What situation led to this decision?

## Decision

What did we decide?

## Consequences

### Positive
- ...

### Negative
- ...

## Alternatives Considered

What else was considered and why was it rejected?
```

---

## Adding a New ADR

1. Create `NNN-short-title.md` (next sequential number)
2. Use the template above
3. Add to the index in this README
4. Reference from relevant code/docs
