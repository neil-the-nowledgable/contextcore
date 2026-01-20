# GitHub Issue: Proposed Blueprint Category - AI Agent Communication

> **Repository**: `open-telemetry/community`
> **Type**: Project Proposal
> **Status**: Draft - Ready for Submission

---

## Issue Title

```
[Project Proposal] AI Agent Communication Blueprint
```

## Issue Body

### Summary

This proposal introduces a new OTel Blueprint category for **AI Agent Communication** — storing agent insights (decisions, lessons, questions) as OpenTelemetry spans to enable persistent memory, cross-session context, and agent coordination.

### Problem Statement

Organizations deploying AI agents face challenges that current Gen AI telemetry doesn't address:

1. **Session-Limited Memory**: Agent decisions and lessons learned disappear when sessions end. Agents repeat context gathering and make inconsistent recommendations.

2. **No Agent Coordination**: Multiple agents working on the same project can't see each other's decisions. Handoffs between agents (or agent-to-human) lose context.

3. **Missing Audit Trail**: "Why did the agent make this decision?" is unanswerable after the session. No visibility into confidence levels or alternatives considered.

### Relationship to Gen AI SemConv

This proposal **complements** existing Gen AI semantic conventions:

| Layer | Focus | Attributes |
|-------|-------|------------|
| **Gen AI SemConv** (existing) | LLM invocations | `gen_ai.system`, `gen_ai.request.model`, token counts |
| **Agent Communication** (proposed) | Agent-level behavior | `agent.insight.type`, `agent.insight.confidence`, session tracking |

```
┌──────────────────────────────────────────────────────────────┐
│  Agent Session Span (proposed)                               │
│  ├── agent.id, agent.session.id, project.id                  │
│  │                                                           │
│  │   ┌──────────────────────────────────────────────────┐    │
│  │   │  LLM Call Span (existing Gen AI)                 │    │
│  │   │  └── gen_ai.system, gen_ai.usage.total_tokens    │    │
│  │   └──────────────────────────────────────────────────┘    │
│  │   ┌──────────────────────────────────────────────────┐    │
│  │   │  Insight Span (proposed)                         │    │
│  │   │  └── agent.insight.type="decision", confidence   │    │
│  │   └──────────────────────────────────────────────────┘    │
│  └───────────────────────────────────────────────────────────┘
```

### Proposed Solution

Store agent insights as spans with standardized semantic conventions:

```yaml
# Agent identity
agent.id: "claude-code"
agent.session.id: "session-123"
agent.type: "development_assistant"

# Insight attributes
agent.insight.type: "decision"     # decision | lesson | question | handoff
agent.insight.summary: "Selected FastAPI for API framework"
agent.insight.confidence: 0.88
agent.insight.rationale: "Better async support, auto OpenAPI generation"
agent.insight.applies_to: ["src/api/"]

# Query prior context
# TraceQL: { agent.insight.type = "decision" && agent.insight.applies_to contains "src/api/" }
```

Key patterns:
- **Insights as Spans**: Decisions, lessons, questions stored in trace backend
- **Prior Context Query**: Agents query before acting, building on previous work
- **Handoff Protocol**: Structured context transfer between agents

### Deliverables

1. **Blueprint Document**: Agent communication patterns (Diagnosis → Guiding Policies → Coherent Actions)
2. **Semantic Conventions**: `agent.*` namespace extensions beyond existing Gen AI
3. **Reference Implementation**: InsightEmitter, InsightQuerier, GuidanceReader
4. **Integration Guide**: How to instrument agent frameworks

### Validation

- [ ] 5+ organizations using AI agents interviewed
- [ ] Problem validation score ≥ 3.5/5.0
- [ ] Solution fit score ≥ 3.5/5.0
- [ ] 2+ reference architecture commitments

*Validation evidence will be attached before final submission.*

### Scope

**In Scope**:
- Agent insight telemetry (decisions, lessons, questions, handoffs)
- Cross-session context persistence and querying
- Agent-to-agent and agent-to-human handoff protocols
- Integration with existing Gen AI semantic conventions

**Out of Scope**:
- LLM-level telemetry (covered by Gen AI SemConv)
- Agent orchestration frameworks (implementation-specific)
- Real-time agent communication (focus is on persistent telemetry)

### Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Gen AI SIG Coordination | 2 weeks | Scope agreement |
| Documentation | 4 weeks | Blueprint document, semconv |
| Reference Implementation | 4 weeks | SDK + examples |
| Community Review | 2 weeks | Feedback incorporation |

### Leadership

- **Proposer**: Neil Yashinsky
- **Sponsorship Sought**: Gen AI SIG, End-User SIG

### Related Work

- [Gen AI Semantic Conventions](https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai)
- [OTel Blueprints Project](https://github.com/open-telemetry/community/blob/main/projects/otel-blueprints.md)
- [ContextCore Agent Module](https://github.com/contextcore/contextcore/tree/main/src/contextcore/agent)

### Success Criteria

1. Blueprint document accepted into OTel documentation
2. `agent.*` namespace extensions proposed to SemConv SIG
3. Coordination with Gen AI SIG on attribute boundaries
4. 3+ organizations adopt patterns within 6 months

---

### Discussion Questions

1. Should agent-level telemetry be part of Gen AI SemConv or a separate namespace?
2. How should this coordinate with the Gen AI SIG's current roadmap?
3. Are there existing agent frameworks we should prioritize integration with?
4. What's the right boundary between LLM telemetry and agent telemetry?

---

/cc @open-telemetry/gen-ai-sig @open-telemetry/end-user-sig
