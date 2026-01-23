# Gap Analysis: ContextCore vs OTel GenAI Semantic Conventions

**Date:** 2026-01-18
**Status:** Draft
**Related Plan:** [OTEL_GENAI_ADOPTION_PLAN.md](OTEL_GENAI_ADOPTION_PLAN.md)

---

## 1. Executive Summary

ContextCore currently uses a custom `agent.*` namespace for agent telemetry. The OpenTelemetry community has recently stabilized the `gen_ai.*` namespace for Generative AI observability. To ensuring interoperability with the broader OTel ecosystem, ContextCore must align with these new conventions while preserving its unique project-management specific attributes.

This analysis identifies the gaps between ContextCore's current implementation and the OTel GenAI semantic conventions (v1.28.0+), proposing a migration path that maintains backward compatibility.

## 2. Attribute Comparison

### 2.1 Agent Identity

| ContextCore Attribute | OTel GenAI Attribute | Status | Recommendation | Complexity (1-5) |
|-----------------------|----------------------|--------|----------------|------------------|
| `agent.id`            | `gen_ai.agent.id`    | Stable | **Alias + Migrate**. Emit both during transition. | 2 |
| `agent.name` (implicit)| `gen_ai.agent.name` | Stable | **Add**. Currently inferred from ID or not present. | 1 |
| `agent.type`          | `gen_ai.agent.description` | No direct match | **Map**. Map `agent.type` to `gen_ai.agent.description` or keep as custom extension. `gen_ai.agent.type` is not standard. | 2 |
| `agent.version`       | - | - | **Keep**. No direct OTel equivalent for agent version yet. | 1 |
| `agent.capabilities`  | - | - | **Keep**. ContextCore specific. | 1 |

**Decision:**
- Adopt `gen_ai.agent.id` and `gen_ai.agent.name`.
- Retain `agent.type` as a valuable classification not covered by OTel.

### 2.2 Session Management

| ContextCore Attribute | OTel GenAI Attribute | Status | Recommendation | Complexity (1-5) |
|-----------------------|----------------------|--------|----------------|------------------|
| `agent.session_id`    | `gen_ai.conversation.id` | Stable | **Migrate**. `gen_ai.conversation.id` is the standard for grouping interactions. | 3 |
| `agent.parent_session_id` | - | - | **Keep/Refine**. OTel uses span parentage, but explicit session linkage is useful. | 2 |

**Decision:**
- Migrate `agent.session_id` to `gen_ai.conversation.id`. This is a critical interoperability change.

### 2.3 Operations & Models

ContextCore currently lacks explicit attributes for the underlying LLM operations, which is a core part of OTel GenAI.

| ContextCore Attribute | OTel GenAI Attribute | Status | Recommendation | Complexity (1-5) |
|-----------------------|----------------------|--------|----------------|------------------|
| -                     | `gen_ai.system`      | Stable | **Add**. Identify provider (e.g., `openai`, `anthropic`). | 2 |
| -                     | `gen_ai.request.model`| Stable | **Add**. Identify model (e.g., `gpt-4o`). | 2 |
| -                     | `gen_ai.operation.name`| Stable | **Add**. Critical for backend grouping (e.g., `chat`, `rag`). | 3 |
| -                     | `gen_ai.token.usage.*`| Stable | **Add**. Standardize token counting if available. | 2 |

**Decision:**
- Implement all above attributes to enable standard "LLM Observability" dashboards to work with ContextCore data.

### 2.4 Handoffs & Tools

ContextCore uses `handoff.*` for agent collaboration. OTel uses `gen_ai.tool.*` for tool execution.

| ContextCore Attribute | OTel GenAI Attribute | Status | Recommendation | Complexity (1-5) |
|-----------------------|----------------------|--------|----------------|------------------|
| `handoff.capability_id`| `gen_ai.tool.name`  | Stable | **Map**. Treat handoffs as tool calls. | 3 |
| `handoff.inputs`      | `gen_ai.tool.call.arguments` | Stable | **Map**. Serialize to JSON if needed. | 3 |
| `handoff.status`      | `error.type` / status | Stable | **Align**. Map failure statuses to OTel span status. | 2 |

**Decision:**
- Model agent handoffs as OTel Tool calls (`gen_ai.operation.name = "tool.call"` maybe? Or just use tool attributes on the handoff span).
- Use `gen_ai.tool.name` for the capability.

## 3. Migration Strategy

### 3.1 Dual-Emit Compatibility Layer

To prevent breaking existing dashboards and queries, we will implement a **Dual-Emit Layer**.

**Mechanism:**
When the code emits `agent.id="claude"`, the layer will automatically emit:
- `agent.id="claude"` (Legacy)
- `gen_ai.agent.id="claude"` (New)

**Configuration:**
Environment variable `CONTEXTCORE_OTEL_MODE`:
- `dual` (Default): Emit both.
- `legacy`: Emit only old attributes.
- `otel`: Emit only new attributes (Target state).

### 3.2 Breaking Changes

1. **Session ID**: Moving from `agent.session_id` to `gen_ai.conversation.id` will break queries relying on the old field if they are not updated. The dual-emit layer mitigates this, but queries must eventually be migrated.
2. **Handoff Structure**: Aligning with tool conventions might change how handoff inputs are stored (e.g. JSON string vs object map).

## 4. Implementation Plan

See [OTEL_GENAI_ADOPTION_PLAN.md](OTEL_GENAI_ADOPTION_PLAN.md) for the execution breakdown.

1. **Gap Analysis** (Completed by this document)
2. **Dual-Emit Layer** implementation
3. **Core Attribute Migration** (`agent.id`, `session_id`)
4. **Operation & Model** enrichment (`gen_ai.system`, `model`)
5. **Tool/Handoff** alignment
6. **Documentation** & Deprecation notices

## 5. References

- [OTel GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [ContextCore Agent Semantic Conventions](agent-semantic-conventions.md)
