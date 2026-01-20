# GitHub Issue: Proposed Semantic Conventions - Agent Insight Namespace

> **Repository**: `open-telemetry/semantic-conventions`
> **Type**: Feature Request / Namespace Extension
> **Status**: Draft - Ready for Submission

---

## Issue Title

```
[Feature] Extend agent.* namespace for AI agent insights and coordination
```

## Issue Body

### Summary

Propose extending the `agent.*` namespace to support AI agent insight telemetry — storing decisions, lessons, questions, and handoffs as spans for persistent memory and agent coordination.

### Relationship to Gen AI SemConv

This proposal **extends** existing Gen AI conventions:

| Layer | Existing | Proposed |
|-------|----------|----------|
| **LLM Call** | `gen_ai.system`, `gen_ai.request.model`, tokens | No change |
| **Agent Session** | - | `agent.id`, `agent.session.id` |
| **Agent Insight** | - | `agent.insight.*` attributes |

The layers are complementary:
```
Agent Session Span (proposed)
├── gen_ai.request span (existing)
├── gen_ai.request span (existing)
├── agent.insight span (proposed)
└── agent.insight span (proposed)
```

### Motivation

Current Gen AI telemetry tracks LLM invocations but not agent-level behavior:

1. **No Persistent Memory**: Agent decisions disappear when sessions end
2. **No Coordination**: Multiple agents can't see each other's decisions
3. **No Audit Trail**: Can't review agent reasoning after the fact
4. **No Handoffs**: Context lost when switching agents or agent-to-human

### Use Cases

1. **Query Prior Decisions**: Before coding, agent queries: `{ agent.insight.type = "decision" && agent.insight.applies_to contains "src/auth/" }`
2. **Audit AI Reasoning**: Compliance review of all agent decisions with confidence scores
3. **Agent Handoff**: Structured context transfer when switching agents
4. **Decision Quality Metrics**: Track average confidence, alternatives considered

### Proposed Attributes

#### Agent Identity

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `agent.id` | string | Unique agent identifier | `"claude-code"` |
| `agent.session.id` | string | Session/conversation ID | `"session-abc123"` |
| `agent.type` | string | Agent category | `"development_assistant"`, `"ops_agent"` |
| `agent.version` | string | Agent/model version | `"1.2.0"` |

#### Insight Core Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `agent.insight.type` | enum | Insight category | `decision`, `lesson`, `question`, `handoff` |
| `agent.insight.summary` | string | Human-readable summary | `"Selected FastAPI for API framework"` |
| `agent.insight.timestamp` | int | Unix timestamp | `1705312800` |

#### Decision-Specific Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `agent.insight.confidence` | float | Confidence score (0.0-1.0) | `0.88` |
| `agent.insight.rationale` | string | Reasoning explanation | `"Better async support"` |
| `agent.insight.alternatives` | string[] | Considered alternatives | `["Flask", "Django"]` |
| `agent.insight.applies_to` | string[] | Files/modules affected | `["src/api/main.py"]` |

#### Lesson-Specific Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `agent.insight.category` | string | Lesson category | `"testing"`, `"architecture"`, `"performance"` |
| `agent.insight.severity` | string | Importance level | `"must_follow"`, `"recommended"` |

#### Question-Specific Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `agent.insight.urgency` | enum | Question urgency | `blocking`, `high`, `medium`, `low` |
| `agent.insight.options` | string[] | Possible answers | `["Option A", "Option B"]` |
| `agent.insight.resolved` | boolean | Whether answered | `false` |
| `agent.insight.answer` | string | Resolution if resolved | `"Go with Option A"` |

#### Handoff-Specific Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `agent.insight.from_agent` | string | Source agent ID | `"claude-session-1"` |
| `agent.insight.to_agent` | string | Target (agent ID or "human") | `"human"` |
| `agent.insight.context_summary` | string | Handoff context | `"Implemented auth, needs tests"` |
| `agent.insight.open_items` | string[] | Remaining work | `["Add unit tests"]` |

### Query Examples

```traceql
# All decisions for a project with high confidence
{ agent.insight.type = "decision" && agent.insight.confidence > 0.8 }

# Lessons learned about testing in last 30 days
{ agent.insight.type = "lesson" && agent.insight.category = "testing" }
| select(agent.insight.summary, agent.insight.applies_to)

# Unresolved blocking questions
{ agent.insight.type = "question" && agent.insight.urgency = "blocking" && agent.insight.resolved = false }

# Handoffs to humans
{ agent.insight.type = "handoff" && agent.insight.to_agent = "human" }
```

### Metrics Derivation

| Metric | Query | Purpose |
|--------|-------|---------|
| `agent.decisions.count` | Count by `agent.id`, `project.id` | Agent activity |
| `agent.decisions.confidence.avg` | Avg `agent.insight.confidence` | Decision quality |
| `agent.questions.unresolved` | Count where `resolved = false` | Human attention needed |
| `agent.handoffs.count` | Count by `from_agent`, `to_agent` | Coordination volume |

### Cardinality Considerations

**Safe for metrics labels**:
- `agent.insight.type` (4 values)
- `agent.insight.category` (bounded enum)
- `agent.insight.urgency` (4 values)
- `agent.id` (bounded by organization)

**High cardinality (span attributes only)**:
- `agent.session.id` (unique per session)
- `agent.insight.summary` (free text)
- `agent.insight.applies_to` (file paths)

### Implementation Example

```python
from opentelemetry import trace

tracer = trace.get_tracer("agent.insights")

# Emit a decision
with tracer.start_as_current_span("agent.insight") as span:
    span.set_attribute("agent.id", "claude-code")
    span.set_attribute("agent.session.id", "session-123")
    span.set_attribute("agent.insight.type", "decision")
    span.set_attribute("agent.insight.summary", "Selected FastAPI for API framework")
    span.set_attribute("agent.insight.confidence", 0.88)
    span.set_attribute("agent.insight.rationale", "Better async support, auto OpenAPI")
    span.set_attribute("agent.insight.applies_to", ["src/api/main.py"])
```

### Prior Art

- **LangSmith**: Tracks LLM chain executions with similar concepts
- **Weights & Biases**: Traces for ML experiments with decision tracking
- **Semantic Kernel**: Agent orchestration with step-level telemetry

### Reference Implementation

[ContextCore Agent Module](https://github.com/contextcore/contextcore/tree/main/src/contextcore/agent):
- `InsightEmitter` — Emit decisions, lessons, questions, handoffs
- `InsightQuerier` — Query prior context via TraceQL
- `GuidanceReader` — Read human-provided constraints

---

### Coordination with Gen AI SIG

This proposal should be reviewed by @open-telemetry/gen-ai-sig to ensure:
1. Namespace boundaries are clear (LLM call vs agent behavior)
2. No conflicts with planned Gen AI conventions
3. Attribute naming follows Gen AI patterns

### Checklist

- [ ] Follows [attribute naming guidelines](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/attribute-naming.md)
- [ ] Relationship to `gen_ai.*` documented
- [ ] Enum values use lowercase with underscores
- [ ] Cardinality documented for metrics safety
- [ ] Query examples provided

---

/cc @open-telemetry/semconv-approvers @open-telemetry/gen-ai-sig
