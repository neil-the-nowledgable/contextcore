# Phase 4: Unified Protocol Alignment

**Goal:** Align ContextCore with both OTel GenAI semantic conventions AND A2A protocol patterns while preserving OTel-native architecture and persistent memory capabilities.

**Date:** 2026-01-20
**Status:** Planning

---

## Executive Summary

This unified plan combines two alignment efforts:

1. **OTel GenAI** - Span attribute semantics (`agent.*` → `gen_ai.*`)
2. **A2A Protocol** - API design, data models, discovery, interoperability

These operate at different layers and are complementary. This plan sequences them for optimal execution.

---

## Workflow Configuration

```python
from startd8.workflows.builtin import LeadContractorWorkflow

DEFAULT_CONFIG = {
    "lead_agent": "anthropic:claude-sonnet-4-20250514",
    "drafter_agent": "openai:gpt-4o-mini",
    "max_iterations": 3,
    "pass_threshold": 80,
}
```

**Estimated Total Cost:** $3.50 - $5.00 (27 tasks)

---

## Execution Phases

| Phase | Name | Tasks | Focus |
|-------|------|-------|-------|
| **1** | Foundation | 2 | Gap analysis, dual-emit layer |
| **2** | API Facades | 4 | A2A-style naming conventions |
| **3** | State Model | 3 | Enhanced handoff states |
| **4** | Core Attributes | 2 | OTel operation name, conversation ID |
| **5** | Discovery | 4 | AgentCard, .well-known endpoints |
| **6** | Part Model | 4 | Unified content types |
| **7** | Extended Attributes | 2 | Provider/model, tool mapping |
| **8** | A2A Adapter | 5 | Protocol bridge |
| **9** | Documentation | 1 | Unified docs update |

**Total:** 27 tasks

---

## Phase 1: Foundation (2 tasks)

These tasks establish the infrastructure needed for all subsequent work.

### Task 1.1: Gap Analysis Document

**Source:** OTel GenAI Task 1
**Priority:** HIGH
**Output:** `docs/OTEL_GENAI_GAP_ANALYSIS.md`

Analyze ContextCore's current semantic conventions against OTel GenAI spec.

```python
TASK_1_1 = {
    "task_description": """
    Analyze ContextCore's current semantic conventions against OTel GenAI conventions.

    INPUTS:
    - ContextCore conventions: docs/semantic-conventions.md, docs/agent-semantic-conventions.md
    - OTel GenAI spec: https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md

    OUTPUT: Gap analysis document with:
    1. Attribute-by-attribute comparison table
    2. Exact mapping recommendations (alias, migrate, add, preserve)
    3. Breaking change assessment
    4. Migration complexity score (1-5) per attribute
    5. Recommended adoption order
    """,
    "context": {
        "contextcore_conventions": "docs/semantic-conventions.md",
        "agent_conventions": "docs/agent-semantic-conventions.md",
    },
    "output_format": "Markdown document with tables",
    "integration_instructions": "Save as docs/OTEL_GENAI_GAP_ANALYSIS.md"
}
```

**Acceptance Criteria:**
- [ ] All current ContextCore attributes mapped
- [ ] All relevant OTel GenAI attributes listed
- [ ] Clear recommendation per attribute
- [ ] Breaking changes identified

---

### Task 1.2: Dual-Emit Compatibility Layer

**Source:** OTel GenAI Task 2
**Priority:** HIGH
**Output:** `src/contextcore/compat/otel_genai.py`

Create compatibility layer that emits both old and new attribute names.

```python
TASK_1_2 = {
    "task_description": """
    Implement a dual-emit compatibility layer for ContextCore that:

    1. Emits BOTH old (agent.*) and new (gen_ai.*) attributes during transition
    2. Is configurable via environment variable: CONTEXTCORE_EMIT_MODE=dual|legacy|otel
    3. Provides deprecation warnings when legacy attributes are queried
    4. Has zero performance overhead when mode=otel (future default)

    IMPLEMENTATION REQUIREMENTS:
    - Create src/contextcore/compat/otel_genai.py
    - Add attribute mapping registry
    - Hook into existing span emission code
    - Add unit tests for all three modes

    EXAMPLE:
    When emitting agent.id="claude-code", also emit gen_ai.agent.id="claude-code"
    """,
    "context": {
        "current_emitter": "src/contextcore/agent/insights.py",
        "tracker": "src/contextcore/tracker.py"
    },
    "output_format": "Python module with tests",
    "integration_instructions": "Integrate with InsightEmitter.emit() and TaskTracker.start_task()"
}
```

**Acceptance Criteria:**
- [ ] Three emit modes working (dual, legacy, otel)
- [ ] Environment variable controls mode
- [ ] Deprecation warnings functional
- [ ] Unit tests pass

---

## Phase 2: API Facades (4 tasks)

Create A2A-style `resource.action` naming for all APIs. These use the dual-emit layer from Phase 1.

### Task 2.1: Insights API Facade

**Source:** A2A Feature 4.1A
**Output:** `src/contextcore/api/insights.py`

```python
TASK_2_1 = {
    "task_description": """
    Create a new facade module that exposes A2A-style naming for the Insights API.

    REQUIREMENTS:
    1. Create src/contextcore/api/insights.py with class InsightsAPI
    2. Methods (map to existing InsightEmitter/InsightQuerier):
       - insights.emit(type, summary, confidence, ...) → InsightEmitter.emit()
       - insights.query(project_id, type, ...) → InsightQuerier.query()
       - insights.get(insight_id) → new method to fetch single insight
       - insights.list(project_id, limit) → alias for query with minimal filters
    3. Use dual-emit layer (CONTEXTCORE_EMIT_MODE) for all span emissions
    4. Preserve existing classes for backward compatibility
    5. Add deprecation warnings to old method names
    6. Export both old and new APIs from __init__.py

    IMPORTANT: Use gen_ai.* attributes when CONTEXTCORE_EMIT_MODE=otel or dual
    """,
    "context": {
        "existing_insights": "src/contextcore/agent/insights.py",
        "compat_layer": "src/contextcore/compat/otel_genai.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/api/__init__.py"
}
```

---

### Task 2.2: Handoffs API Facade

**Source:** A2A Feature 4.1B
**Output:** `src/contextcore/api/handoffs.py`

```python
TASK_2_2 = {
    "task_description": """
    Create a new facade module that exposes A2A-style naming for the Handoffs API.

    REQUIREMENTS:
    1. Create src/contextcore/api/handoffs.py with class HandoffsAPI
    2. Methods (map to existing HandoffManager/HandoffReceiver):
       - handoffs.create(to_agent, capability_id, task, inputs, ...) → create_handoff()
       - handoffs.get(handoff_id) → get_handoff_status()
       - handoffs.await(handoff_id, timeout_ms) → await_result()
       - handoffs.cancel(handoff_id) → new method
       - handoffs.accept(handoff_id) → HandoffReceiver.accept()
       - handoffs.complete(handoff_id, result_trace_id) → complete()
       - handoffs.fail(handoff_id, reason) → fail()
       - handoffs.subscribe(project_id) → poll_handoffs() as generator
    3. Add handoffs.send() as alias for create() + await() (matches A2A message.send)
    4. Use dual-emit layer for span emissions
    5. Export from __init__.py
    """,
    "context": {
        "existing_handoff": "src/contextcore/agent/handoff.py",
        "compat_layer": "src/contextcore/compat/otel_genai.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/api/__init__.py"
}
```

---

### Task 2.3: Skills API Facade

**Source:** A2A Feature 4.1C
**Output:** `src/contextcore/api/skills.py`

```python
TASK_2_3 = {
    "task_description": """
    Create a new facade module that exposes A2A-style naming for the Skills API.

    REQUIREMENTS:
    1. Create src/contextcore/api/skills.py with class SkillsAPI
    2. Methods (map to existing SkillCapabilityEmitter/Querier):
       - skills.emit(manifest, capabilities) → emit_skill_with_capabilities()
       - skills.query(trigger, category, budget) → querier methods
       - skills.get(skill_id) → fetch single skill manifest
       - skills.list() → list all registered skills
       - capabilities.emit(skill_id, capability) → emit_capability()
       - capabilities.invoke(skill_id, capability_id, inputs) → emit_invoked()
       - capabilities.complete(skill_id, capability_id, outputs) → emit_succeeded()
       - capabilities.fail(skill_id, capability_id, error) → emit_failed()
    3. Use dual-emit layer for span emissions
    4. Export from __init__.py
    """,
    "context": {
        "existing_skill": "src/contextcore/skill/",
        "compat_layer": "src/contextcore/compat/otel_genai.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/api/__init__.py"
}
```

---

### Task 2.4: API Package Init

**Source:** A2A Feature 4.1D
**Output:** `src/contextcore/api/__init__.py`

```python
TASK_2_4 = {
    "task_description": """
    Create the unified API package that exports all facades.

    REQUIREMENTS:
    1. Create src/contextcore/api/__init__.py
    2. Export all API classes: InsightsAPI, HandoffsAPI, SkillsAPI
    3. Create convenience factory functions:
       - create_insights_api(project_id, agent_id) → configured InsightsAPI
       - create_handoffs_api(project_id, agent_id) → configured HandoffsAPI
       - create_skills_api(agent_id) → configured SkillsAPI
    4. Create unified ContextCoreAPI class that combines all three
    5. Example usage in docstring:
       ```python
       from contextcore.api import ContextCoreAPI

       api = ContextCoreAPI(project_id="checkout", agent_id="claude-code")
       api.insights.emit(type="decision", summary="...", confidence=0.9)
       api.handoffs.create(to_agent="o11y", capability_id="investigate", ...)
       api.skills.query(trigger="format")
       ```
    """,
    "output_format": "Python module",
    "integration_instructions": "Add to src/contextcore/__init__.py exports"
}
```

---

## Phase 3: State Model Enhancement (3 tasks)

Enhance handoff states with A2A-aligned additions.

### Task 3.1: Enhanced HandoffStatus

**Source:** A2A Feature 4.2A
**Output:** Updated `src/contextcore/agent/handoff.py`

```python
TASK_3_1 = {
    "task_description": """
    Extend HandoffStatus enum with A2A-aligned states.

    REQUIREMENTS:
    1. Update src/contextcore/agent/handoff.py HandoffStatus enum:
       class HandoffStatus(str, Enum):
           # Existing states
           PENDING = "pending"
           ACCEPTED = "accepted"
           IN_PROGRESS = "in_progress"
           COMPLETED = "completed"
           FAILED = "failed"
           TIMEOUT = "timeout"
           # NEW: A2A-aligned states
           INPUT_REQUIRED = "input_required"  # Agent needs clarification
           CANCELLED = "cancelled"            # Client-requested termination
           REJECTED = "rejected"              # Agent refused task

    2. Add helper methods:
       - is_terminal() -> bool: True for COMPLETED, FAILED, TIMEOUT, CANCELLED, REJECTED
       - is_active() -> bool: True for PENDING, ACCEPTED, IN_PROGRESS, INPUT_REQUIRED
       - can_transition_to(target: HandoffStatus) -> bool: validates transitions

    3. Define valid state transitions:
       - PENDING → ACCEPTED, REJECTED, CANCELLED
       - ACCEPTED → IN_PROGRESS, CANCELLED
       - IN_PROGRESS → INPUT_REQUIRED, COMPLETED, FAILED, CANCELLED
       - INPUT_REQUIRED → IN_PROGRESS, COMPLETED, FAILED, CANCELLED

    4. Update HandoffManager and HandoffReceiver to support new states
    """,
    "context": {
        "existing_handoff": "src/contextcore/agent/handoff.py"
    },
    "output_format": "Updated Python module",
    "integration_instructions": "Ensure backward compatibility with existing status values"
}
```

---

### Task 3.2: State Transition Events

**Source:** A2A Feature 4.2B
**Output:** `src/contextcore/agent/events.py`

```python
TASK_3_2 = {
    "task_description": """
    Create state transition event model for tracking handoff lifecycle.

    REQUIREMENTS:
    1. Create src/contextcore/agent/events.py with:
       class HandoffEventType(str, Enum):
           STATUS_UPDATE = "handoff.status_update"
           INPUT_REQUIRED = "handoff.input_required"
           ARTIFACT_ADDED = "handoff.artifact_added"
           MESSAGE_ADDED = "handoff.message_added"

       @dataclass
       class HandoffEvent:
           event_type: HandoffEventType
           handoff_id: str
           timestamp: datetime
           from_status: HandoffStatus | None
           to_status: HandoffStatus | None
           message: str | None = None
           metadata: dict[str, Any] = field(default_factory=dict)

    2. Create HandoffEventEmitter class:
       - emit_status_update(handoff_id, from_status, to_status) - emits OTel span event
       - emit_input_required(handoff_id, question, options) - emits input request
       - emit_artifact_added(handoff_id, artifact_id, artifact_type) - emits artifact event

    3. Integrate with HandoffManager to emit events on state changes
    4. Use dual-emit layer for gen_ai.* attribute emission
    """,
    "context": {
        "handoff": "src/contextcore/agent/handoff.py",
        "compat_layer": "src/contextcore/compat/otel_genai.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Hook into HandoffManager state transitions"
}
```

---

### Task 3.3: Input Request Model

**Source:** A2A Feature 4.2C
**Output:** `src/contextcore/agent/input_request.py`

```python
TASK_3_3 = {
    "task_description": """
    Create model for INPUT_REQUIRED state requests.

    REQUIREMENTS:
    1. Create src/contextcore/agent/input_request.py with:
       @dataclass
       class InputOption:
           value: str
           label: str
           description: str | None = None

       class InputType(str, Enum):
           TEXT = "text"
           CHOICE = "choice"
           MULTI_CHOICE = "multi_choice"
           CONFIRMATION = "confirmation"
           FILE = "file"

       @dataclass
       class InputRequest:
           request_id: str
           handoff_id: str
           question: str
           input_type: InputType
           options: list[InputOption] | None = None
           default_value: str | None = None
           required: bool = True
           timeout_ms: int = 300000
           created_at: datetime

    2. Add methods to HandoffReceiver:
       - request_input(handoff_id, question, input_type, options) - creates InputRequest
       - provide_input(handoff_id, request_id, value) - provides response

    3. Store InputRequests in storage backend
    """,
    "context": {
        "handoff": "src/contextcore/agent/handoff.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/agent/__init__.py"
}
```

---

## Phase 4: Core OTel Attributes (2 tasks)

Add critical OTel GenAI attributes to all spans.

### Task 4.1: gen_ai.operation.name Support

**Source:** OTel GenAI Task 3
**Output:** Updated span emission code

```python
TASK_4_1 = {
    "task_description": """
    Add gen_ai.operation.name attribute to all ContextCore span types.

    OPERATION MAPPINGS:
    - Task spans: operation.name = "task.{action}" (task.start, task.update, task.complete)
    - Insight spans: operation.name = "insight.emit"
    - Handoff spans: operation.name = "handoff.{status}" (handoff.request, handoff.complete)
    - Skill spans: operation.name = "skill.invoke", "skill.complete"
    - Verification spans: operation.name = "install.verify"

    IMPLEMENTATION:
    - Update TaskTracker to emit gen_ai.operation.name
    - Update InsightEmitter to emit gen_ai.operation.name
    - Update HandoffManager to emit gen_ai.operation.name
    - Update SkillCapabilityEmitter to emit gen_ai.operation.name

    Use dual-emit layer - emit only when CONTEXTCORE_EMIT_MODE=dual|otel
    """,
    "context": {
        "tracker": "src/contextcore/tracker.py",
        "insights": "src/contextcore/agent/insights.py",
        "handoff": "src/contextcore/agent/handoff.py",
        "skill": "src/contextcore/skill/emitter.py",
        "compat_layer": "src/contextcore/compat/otel_genai.py"
    },
    "output_format": "Code changes with tests",
    "integration_instructions": "Update semantic-conventions.md with new attributes"
}
```

---

### Task 4.2: gen_ai.conversation.id Migration

**Source:** OTel GenAI Task 6
**Output:** Updated code using conversation_id

```python
TASK_4_2 = {
    "task_description": """
    Replace agent.session_id with gen_ai.conversation.id per OTel conventions.

    MIGRATION:
    - agent.session_id → gen_ai.conversation.id
    - Keep agent.session_id as alias during transition (dual-emit)
    - Update all code references
    - Update CLI commands
    - Update documentation

    IMPORTANT: This affects the Message model being created in Phase 6.
    Ensure new models use conversation_id field name, not session_id.

    The conversation.id represents the session/thread that groups related
    agent interactions, aligning with OTel's concept.
    """,
    "context": {
        "insights": "src/contextcore/agent/insights.py",
        "cli": "src/contextcore/cli/",
        "compat_layer": "src/contextcore/compat/otel_genai.py"
    },
    "output_format": "Code changes with tests",
    "integration_instructions": "Add migration note to CHANGELOG"
}
```

---

## Phase 5: Discovery (4 tasks)

Implement A2A-compatible agent discovery with ContextCore extensions.

### Task 5.1: AgentCard Model

**Source:** A2A Feature 4.3A
**Output:** `src/contextcore/discovery/agent_card.py`

```python
TASK_5_1 = {
    "task_description": """
    Create AgentCard model compatible with A2A specification plus ContextCore extensions.

    REQUIREMENTS:
    1. Create src/contextcore/discovery/agent_card.py with dataclasses:
       - AgentCapabilities (A2A standard + CC extensions: insights, handoffs, skills, otel_native)
       - SkillDescriptor (A2A-compatible skill definition)
       - AuthScheme enum (Bearer, Basic, ApiKey, OAuth2, None)
       - AuthConfig (schemes, credentials_url, oauth2_config)
       - ProviderInfo (organization, url, contact)
       - AgentCard (full model with A2A fields + CC extensions)

    2. AgentCard must include:
       - A2A required: agent_id, name, description, url, version, capabilities, skills
       - A2A optional: authentication, default_input_modes, default_output_modes, provider
       - CC extensions: tempo_url, traceql_prefix, project_refs

    3. Methods:
       - to_a2a_json() - export as A2A-compatible JSON (no CC extensions)
       - to_contextcore_json() - export with CC extensions
       - from_json(data) - parse from JSON (handles both formats)
       - from_skill_manifest(manifest, agent_id, url) - create from existing SkillManifest
    """,
    "context": {
        "skill_models": "src/contextcore/skill/models.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/discovery/__init__.py"
}
```

---

### Task 5.2: Discovery Endpoint

**Source:** A2A Feature 4.3B
**Output:** `src/contextcore/discovery/endpoint.py`

```python
TASK_5_2 = {
    "task_description": """
    Create well-known discovery endpoint handler for serving agent cards.

    REQUIREMENTS:
    1. Create src/contextcore/discovery/endpoint.py with:
       - DiscoveryDocument dataclass (version, protocol, agent, discovery, endpoints)
       - DiscoveryEndpoint class

    2. DiscoveryEndpoint methods:
       - get_a2a_agent_json() - returns A2A-compatible agent.json
       - get_contextcore_json() - returns full CC discovery document
       - get_well_known_paths() - returns mapping of paths to handlers

    3. Optional framework integrations:
       - create_discovery_blueprint(endpoint) - Flask blueprint factory
       - create_discovery_router(endpoint) - FastAPI router factory

    4. Serve at:
       - /.well-known/agent.json (A2A standard)
       - /.well-known/contextcore.json (CC extended)
    """,
    "context": {
        "agent_card": "src/contextcore/discovery/agent_card.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/discovery/__init__.py"
}
```

---

### Task 5.3: Discovery Client

**Source:** A2A Feature 4.3C
**Output:** `src/contextcore/discovery/client.py`

```python
TASK_5_3 = {
    "task_description": """
    Create client for discovering remote agents via HTTP and Tempo.

    REQUIREMENTS:
    1. Create src/contextcore/discovery/client.py with DiscoveryClient class

    2. HTTP discovery methods:
       - discover(base_url) - fetch AgentCard (try CC endpoint, fall back to A2A)
       - _fetch_contextcore_card(base_url) - fetch CC discovery document
       - _fetch_a2a_card(base_url) - fetch A2A agent.json

    3. Tempo-based discovery (ContextCore-native):
       - discover_from_tempo(agent_id) - build AgentCard from skill spans
       - list_agents_from_tempo(time_range) - list all agent IDs in Tempo

    4. Cache management:
       - get_cached(agent_id) - get from cache if not expired
       - invalidate(agent_id) - remove from cache
       - clear_cache() - clear all
       - list_known_agents() - return all cached agents

    5. Context manager for HTTP client lifecycle
    6. Graceful error handling (return None for unreachable agents)
    """,
    "context": {
        "agent_card": "src/contextcore/discovery/agent_card.py"
    },
    "output_format": "Python module with httpx",
    "integration_instructions": "Export from src/contextcore/discovery/__init__.py"
}
```

---

### Task 5.4: Discovery Package and CLI

**Source:** A2A Feature 4.3D
**Output:** `src/contextcore/discovery/__init__.py`, `src/contextcore/cli/discovery.py`

```python
TASK_5_4 = {
    "task_description": """
    Create discovery package with CLI integration.

    REQUIREMENTS:
    1. Create src/contextcore/discovery/__init__.py exporting all public classes

    2. Create src/contextcore/cli/discovery.py with Click commands:
       a) card - Generate AgentCard:
          contextcore discovery card --agent-id X --name Y --url Z --output agent.json

       b) serve - Start discovery server:
          contextcore discovery serve --port 8080 --agent-card agent.json

       c) fetch - Fetch remote AgentCard:
          contextcore discovery fetch --url https://agent.example.com

       d) list - List agents from Tempo:
          contextcore discovery list --tempo-url http://localhost:3200 --time-range 24h

    3. Register discovery group with main CLI
    """,
    "output_format": "Python modules",
    "integration_instructions": "Add discovery group to src/contextcore/cli/__init__.py"
}
```

---

## Phase 6: Part Model Unification (4 tasks)

Unify content types into A2A-compatible Part model.

### Task 6.1: Unified Part Model

**Source:** A2A Feature 4.4A
**Output:** `src/contextcore/models/part.py`

```python
TASK_6_1 = {
    "task_description": """
    Create unified Part model supporting both A2A and ContextCore content types.

    REQUIREMENTS:
    1. Create src/contextcore/models/part.py with:
       - PartType enum (A2A: TEXT, FILE, DATA, JSON, FORM + CC: TRACE, LOG_QUERY, etc.)
       - Part dataclass with all content fields

    2. Part must support:
       - Text content (text field)
       - File content (file_uri, mime_type)
       - Structured data (data dict)
       - CC observability (trace_id, span_id, query)
       - References (ref, description)
       - Token budget (tokens - CC extension)

    3. Methods:
       - to_a2a_dict() - convert to A2A Part format
       - to_evidence() - convert to legacy Evidence format
       - from_evidence(evidence) - create from legacy Evidence

    4. Factory methods:
       - Part.text_part(text) - create text part
       - Part.trace_part(trace_id, description) - create trace reference
       - Part.file_part(uri, mime_type) - create file part
       - Part.query_part(query, query_type) - create query part (TraceQL, LogQL, PromQL)
    """,
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/models/__init__.py"
}
```

---

### Task 6.2: Message Model

**Source:** A2A Feature 4.4B
**Output:** `src/contextcore/models/message.py`

```python
TASK_6_2 = {
    "task_description": """
    Create A2A-compatible Message model for handoff communication.

    REQUIREMENTS:
    1. Create src/contextcore/models/message.py with:
       - MessageRole enum (USER, AGENT, SYSTEM)
       - Message dataclass

    2. Message fields:
       - message_id: str
       - role: MessageRole
       - parts: list[Part]
       - timestamp: datetime
       - CC extensions:
         - agent_id: str | None
         - conversation_id: str | None  # Use conversation_id, NOT session_id (OTel aligned)
         - metadata: dict

    3. Methods:
       - to_a2a_dict() - convert to A2A Message format
       - from_text(text, role) - create message from plain text

    4. Update Handoff model to include messages: list[Message] field

    IMPORTANT: Use conversation_id field name to align with gen_ai.conversation.id
    """,
    "context": {
        "part": "src/contextcore/models/part.py",
        "handoff": "src/contextcore/agent/handoff.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/models/__init__.py"
}
```

---

### Task 6.3: Artifact Model

**Source:** A2A Feature 4.4C
**Output:** `src/contextcore/models/artifact.py`

```python
TASK_6_3 = {
    "task_description": """
    Create A2A-compatible Artifact model for handoff outputs.

    REQUIREMENTS:
    1. Create src/contextcore/models/artifact.py with Artifact dataclass:
       - artifact_id: str
       - parts: list[Part]
       - media_type: str = "application/json"
       - index: int = 0
       - append: bool = False
       - last_chunk: bool = True
       - CC extensions:
         - trace_id: str | None (link to OTel trace)
         - metadata: dict

    2. Methods:
       - to_a2a_dict() - convert to A2A Artifact format
       - from_insight(insight) - create artifact from Insight
       - from_json(data, artifact_id) - create from JSON data

    3. Update Handoff model to include artifacts: list[Artifact] field
    """,
    "context": {
        "part": "src/contextcore/models/part.py",
        "insight": "src/contextcore/agent/insights.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/models/__init__.py"
}
```

---

### Task 6.4: Models Package Init

**Source:** A2A Feature 4.4D
**Output:** `src/contextcore/models/__init__.py`

```python
TASK_6_4 = {
    "task_description": """
    Create models package with backward compatibility.

    REQUIREMENTS:
    1. Create src/contextcore/models/__init__.py exporting:
       - Part, PartType
       - Message, MessageRole
       - Artifact
       - Legacy Evidence (re-exported for backward compatibility)

    2. Add Evidence as deprecated alias:
       Evidence = Part  # with deprecation warning on access

    3. Update src/contextcore/agent/insights.py to use Part internally
       while maintaining Evidence API for backward compatibility

    4. Add __all__ with all exports
    """,
    "context": {
        "insights": "src/contextcore/agent/insights.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Add models to src/contextcore/__init__.py exports"
}
```

---

## Phase 7: Extended OTel Attributes (2 tasks)

Add provider/model tracking and tool mapping.

### Task 7.1: Provider and Model Tracking

**Source:** OTel GenAI Task 4
**Output:** Updated insight emission code

```python
TASK_7_1 = {
    "task_description": """
    Add provider and model tracking to insight spans.

    When an agent emits an insight, capture:
    - gen_ai.provider.name: "anthropic", "openai", "google", etc.
    - gen_ai.request.model: "claude-opus-4-5-20251101", "gpt-4o", etc.

    IMPLEMENTATION:
    - Add optional provider/model params to InsightEmitter and InsightsAPI
    - Auto-detect from environment if not provided:
      - Check OTEL_SERVICE_NAME for patterns like "claude-*", "gpt-*"
      - Check LLM_PROVIDER, LLM_MODEL env vars
    - Store in span attributes via dual-emit layer

    This enables queries like:
    - "Show me all decisions made by Claude Opus"
    - "Compare insight confidence by model"
    - { gen_ai.provider.name = "anthropic" && insight.type = "decision" }
    """,
    "context": {
        "insights": "src/contextcore/agent/insights.py",
        "api_insights": "src/contextcore/api/insights.py",
        "compat_layer": "src/contextcore/compat/otel_genai.py"
    },
    "output_format": "Code changes with tests",
    "integration_instructions": "Add CLI: contextcore insight emit --provider anthropic --model claude-opus-4-5"
}
```

---

### Task 7.2: Tool Mapping for Handoffs

**Source:** OTel GenAI Task 5
**Output:** Updated handoff emission code

```python
TASK_7_2 = {
    "task_description": """
    Map ContextCore handoff attributes to OTel gen_ai.tool.* conventions.

    CURRENT → NEW MAPPING:
    - handoff.capability_id → gen_ai.tool.name
    - handoff.inputs → gen_ai.tool.call.arguments (JSON)
    - handoff.expected_output → (keep, no OTel equivalent)
    - handoff.status → gen_ai.tool.call.result (on completion)
    - (new) gen_ai.tool.type = "agent_handoff"
    - (new) gen_ai.tool.call.id = handoff.id

    IMPLEMENTATION:
    - Update HandoffManager to emit both old and new attributes via dual-emit layer
    - Update handoff completion to record result as gen_ai.tool.call.result
    - Document tool.type="agent_handoff" as ContextCore extension
    """,
    "context": {
        "handoff": "src/contextcore/agent/handoff.py",
        "api_handoffs": "src/contextcore/api/handoffs.py",
        "compat_layer": "src/contextcore/compat/otel_genai.py"
    },
    "output_format": "Code changes with tests",
    "integration_instructions": "Document in agent-semantic-conventions.md"
}
```

---

## Phase 8: A2A Protocol Adapter (5 tasks)

Create adapter layer for bidirectional A2A protocol support.

### Task 8.1: Task Adapter

**Source:** A2A Feature 4.5A
**Output:** `src/contextcore/a2a/task_adapter.py`

```python
TASK_8_1 = {
    "task_description": """
    Create adapter to translate between A2A Task and ContextCore Handoff.

    REQUIREMENTS:
    1. Create src/contextcore/a2a/task_adapter.py with TaskAdapter class

    2. Methods:
       - handoff_to_task(handoff) - convert CC Handoff to A2A Task JSON
       - task_to_handoff(task, from_agent, to_agent) - convert A2A Task to CC Handoff
       - _status_to_task_state(status) - map HandoffStatus to A2A TaskState
       - _task_state_to_status(state) - map A2A TaskState to HandoffStatus

    3. Status mapping:
       - PENDING → PENDING
       - ACCEPTED, IN_PROGRESS → WORKING
       - INPUT_REQUIRED → INPUT_REQUIRED
       - COMPLETED → COMPLETED
       - FAILED, TIMEOUT → FAILED
       - CANCELLED → CANCELLED
       - REJECTED → REJECTED

    4. Task JSON must include: taskId, contextId, status, messages, artifacts, timestamps
    """,
    "context": {
        "handoff": "src/contextcore/agent/handoff.py",
        "message": "src/contextcore/models/message.py",
        "artifact": "src/contextcore/models/artifact.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/a2a/__init__.py"
}
```

---

### Task 8.2: A2A Message Handler

**Source:** A2A Feature 4.5B
**Output:** `src/contextcore/a2a/message_handler.py`

```python
TASK_8_2 = {
    "task_description": """
    Create JSON-RPC message handler for A2A protocol methods.

    REQUIREMENTS:
    1. Create src/contextcore/a2a/message_handler.py with A2AMessageHandler class

    2. Initialize with HandoffsAPI and SkillsAPI instances

    3. Supported methods:
       - message.send → creates handoff, waits for result
       - tasks.get → returns task/handoff status
       - tasks.list → lists tasks for context
       - tasks.cancel → cancels task/handoff
       - agent.getExtendedAgentCard → returns extended agent card

    4. handle(request) method:
       - Parse JSON-RPC 2.0 request
       - Route to appropriate handler
       - Return JSON-RPC 2.0 response
       - Handle errors with proper error codes (-32601 method not found, etc.)
    """,
    "context": {
        "api_handoffs": "src/contextcore/api/handoffs.py",
        "api_skills": "src/contextcore/api/skills.py",
        "task_adapter": "src/contextcore/a2a/task_adapter.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/a2a/__init__.py"
}
```

---

### Task 8.3: A2A Server

**Source:** A2A Feature 4.5C
**Output:** `src/contextcore/a2a/server.py`

```python
TASK_8_3 = {
    "task_description": """
    Create HTTP server that speaks A2A protocol.

    REQUIREMENTS:
    1. Create src/contextcore/a2a/server.py with A2AServer class

    2. Initialize with:
       - agent_card: AgentCard
       - handoffs_api: HandoffsAPI
       - skills_api: SkillsAPI
       - host, port configuration

    3. Routes:
       - GET /.well-known/agent.json → A2A agent card (from DiscoveryEndpoint)
       - GET /.well-known/contextcore.json → CC discovery (from DiscoveryEndpoint)
       - POST /a2a → JSON-RPC handler (A2AMessageHandler)
       - GET /a2a/sse/{task_id} → SSE streaming (optional, for push notifications)

    4. create_app() method - returns WSGI/ASGI app (Flask or FastAPI)
    5. run() method - starts the server

    6. CLI integration: contextcore a2a serve --port 8080
    """,
    "context": {
        "message_handler": "src/contextcore/a2a/message_handler.py",
        "discovery": "src/contextcore/discovery/endpoint.py"
    },
    "output_format": "Python module",
    "integration_instructions": "Export from src/contextcore/a2a/__init__.py"
}
```

---

### Task 8.4: A2A Client

**Source:** A2A Feature 4.5D
**Output:** `src/contextcore/a2a/client.py`

```python
TASK_8_4 = {
    "task_description": """
    Create client for communicating with A2A-compatible agents.

    REQUIREMENTS:
    1. Create src/contextcore/a2a/client.py with A2AClient class

    2. Initialize with base_url and optional AuthConfig

    3. Methods:
       - send_message(message, context_id) → send message.send request
       - get_task(task_id) → get task status via tasks.get
       - list_tasks(context_id) → list tasks via tasks.list
       - cancel_task(task_id) → cancel via tasks.cancel
       - get_agent_card() → fetch from .well-known/agent.json

    4. Convenience method:
       - send_and_convert(message) → send message and convert response to CC Handoff

    5. Use httpx for HTTP client
    6. Handle authentication per AuthConfig

    7. CLI integration: contextcore a2a send --url URL --message "text"
    """,
    "context": {
        "task_adapter": "src/contextcore/a2a/task_adapter.py",
        "message": "src/contextcore/models/message.py",
        "discovery": "src/contextcore/discovery/agent_card.py"
    },
    "output_format": "Python module with httpx",
    "integration_instructions": "Export from src/contextcore/a2a/__init__.py"
}
```

---

### Task 8.5: A2A Package and CLI

**Source:** A2A Feature 4.5E
**Output:** `src/contextcore/a2a/__init__.py`, `src/contextcore/cli/a2a.py`

```python
TASK_8_5 = {
    "task_description": """
    Create A2A package with full exports and CLI.

    REQUIREMENTS:
    1. Create src/contextcore/a2a/__init__.py exporting:
       - TaskAdapter
       - A2AMessageHandler
       - A2AServer
       - A2AClient

    2. Create src/contextcore/cli/a2a.py with Click commands:
       a) serve - Start A2A server:
          contextcore a2a serve --port 8080 --agent-id X --agent-card agent.json

       b) send - Send message to remote agent:
          contextcore a2a send --url URL --message "text" [--context-id X]

       c) status - Get task status:
          contextcore a2a status --url URL --task-id X

       d) cancel - Cancel task:
          contextcore a2a cancel --url URL --task-id X

    3. Register a2a group with main CLI
    """,
    "output_format": "Python modules",
    "integration_instructions": "Add a2a group to src/contextcore/cli/__init__.py"
}
```

---

## Phase 9: Documentation (1 task)

### Task 9.1: Unified Documentation Update

**Source:** OTel GenAI Task 7 + A2A docs
**Output:** Updated documentation files

```python
TASK_9_1 = {
    "task_description": """
    Comprehensive documentation update reflecting both OTel and A2A alignment.

    DOCUMENTATION UPDATES:

    1. docs/semantic-conventions.md:
       - Add "OTel GenAI Alignment" section
       - Document all gen_ai.* attributes used
       - Show mapping from ContextCore-specific to OTel

    2. docs/agent-semantic-conventions.md:
       - Update attribute tables with OTel equivalents
       - Add dual-emit mode documentation
       - Update query examples to show both legacy and OTel attributes

    3. New: docs/OTEL_GENAI_MIGRATION_GUIDE.md:
       - Step-by-step migration for existing users
       - Query migration examples (old → new TraceQL)
       - Timeline for deprecation of legacy attributes
       - CONTEXTCORE_EMIT_MODE configuration

    4. New: docs/A2A_INTEROPERABILITY.md:
       - A2A protocol overview
       - AgentCard configuration
       - Discovery endpoint setup
       - Client/server usage examples
       - Handoff ↔ Task mapping reference

    5. Update README.md:
       - Add OTel GenAI compliance badge/note
       - Add A2A interoperability section
       - Link to new docs

    TONE: Position ContextCore as "OTel GenAI conventions + A2A interoperability + project management extensions"
    """,
    "context": {
        "semantic_conventions": "docs/semantic-conventions.md",
        "agent_conventions": "docs/agent-semantic-conventions.md",
        "readme": "README.md"
    },
    "output_format": "Markdown documents",
    "integration_instructions": "Add links to CLAUDE.md documentation section"
}
```

---

## Execution Commands

```bash
# Run entire unified plan
python3 scripts/lead_contractor/run_unified.py

# Run specific phase
python3 scripts/lead_contractor/run_unified.py --phase 1  # Foundation
python3 scripts/lead_contractor/run_unified.py --phase 2  # API Facades
python3 scripts/lead_contractor/run_unified.py --phase 3  # State Model
python3 scripts/lead_contractor/run_unified.py --phase 4  # Core Attributes
python3 scripts/lead_contractor/run_unified.py --phase 5  # Discovery
python3 scripts/lead_contractor/run_unified.py --phase 6  # Part Model
python3 scripts/lead_contractor/run_unified.py --phase 7  # Extended Attributes
python3 scripts/lead_contractor/run_unified.py --phase 8  # A2A Adapter
python3 scripts/lead_contractor/run_unified.py --phase 9  # Documentation

# Run specific task
python3 scripts/lead_contractor/run_unified.py --phase 1 --task 2

# List all tasks
python3 scripts/lead_contractor/run_unified.py --list
```

---

## Summary

| Phase | Tasks | Source | Key Outputs |
|-------|-------|--------|-------------|
| 1. Foundation | 2 | OTel | Gap analysis, dual-emit layer |
| 2. API Facades | 4 | A2A | InsightsAPI, HandoffsAPI, SkillsAPI |
| 3. State Model | 3 | A2A | Enhanced HandoffStatus, events, input requests |
| 4. Core Attributes | 2 | OTel | operation.name, conversation.id |
| 5. Discovery | 4 | A2A | AgentCard, endpoints, client, CLI |
| 6. Part Model | 4 | A2A | Part, Message, Artifact, models package |
| 7. Extended Attributes | 2 | OTel | Provider/model tracking, tool mapping |
| 8. A2A Adapter | 5 | A2A | TaskAdapter, handler, server, client |
| 9. Documentation | 1 | Both | Unified docs update |

**Total: 27 tasks**
**Estimated Cost: $3.50 - $5.00**

---

## Success Criteria

1. **OTel Compliance**: All spans emit gen_ai.* attributes (when mode=otel|dual)
2. **A2A Interop**: Can communicate with A2A-compatible agents
3. **API Consistency**: All APIs follow resource.action naming pattern
4. **Backward Compatibility**: Existing code continues to work (dual-emit, deprecation warnings)
5. **Discovery**: AgentCard served at .well-known endpoints
6. **State Machine**: INPUT_REQUIRED, CANCELLED, REJECTED states functional
7. **Documentation**: Complete migration guides for both OTel and A2A

---

## Dependencies

- Python 3.9+
- httpx (HTTP client for discovery and A2A client)
- Flask or FastAPI (optional, for A2A server)
- Existing ContextCore modules
- startd8 SDK (Lead Contractor workflow)
