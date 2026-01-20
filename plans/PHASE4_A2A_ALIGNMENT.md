# Phase 4: A2A Protocol Alignment

**Goal:** Adopt A2A naming conventions, discovery patterns, and state model enhancements while preserving ContextCore's OTel-native architecture and persistent memory capabilities.

**Approach:** Use the startd8 SDK Lead Contractor workflow to generate production-ready code for each feature.

---

## Overview

This phase aligns ContextCore with the [A2A Protocol](https://a2a-protocol.org) to enable interoperability while maintaining ContextCore's unique strengths:
- OTel-native telemetry storage
- TraceQL-based discovery
- Persistent agent memory (Insights, Lessons)
- Human-in-the-loop guidance

---

## Feature Groups

| Group | Features | Language | Output Directory |
|-------|----------|----------|------------------|
| 4.1 | Naming Convention Migration | Python | `src/contextcore/` |
| 4.2 | State Model Enhancement | Python | `src/contextcore/agent/` |
| 4.3 | AgentCard & Discovery | Python | `src/contextcore/discovery/` |
| 4.4 | Part Model Unification | Python | `src/contextcore/models/` |
| 4.5 | A2A Protocol Adapter | Python | `src/contextcore/a2a/` |

---

## Feature 4.1: Naming Convention Migration

Migrate ContextCore APIs to A2A-style `resource.action` naming while maintaining backward compatibility.

### Feature 4.1A: Insights API Facade

**Task:** Create a new facade module that exposes A2A-style naming for the Insights API.

**Requirements:**
1. Create `src/contextcore/api/insights.py` with class `InsightsAPI`
2. Methods (map to existing InsightEmitter/InsightQuerier):
   - `insights.emit(type, summary, confidence, ...)` → `InsightEmitter.emit()`
   - `insights.query(project_id, type, ...)` → `InsightQuerier.query()`
   - `insights.get(insight_id)` → new method to fetch single insight
   - `insights.list(project_id, limit)` → alias for query with minimal filters
3. Preserve existing classes for backward compatibility
4. Add deprecation warnings to old method names
5. Export both old and new APIs from `__init__.py`

**Output:** `src/contextcore/api/insights.py`

---

### Feature 4.1B: Handoffs API Facade

**Task:** Create a new facade module that exposes A2A-style naming for the Handoffs API.

**Requirements:**
1. Create `src/contextcore/api/handoffs.py` with class `HandoffsAPI`
2. Methods (map to existing HandoffManager/HandoffReceiver):
   - `handoffs.create(to_agent, capability_id, task, inputs, ...)` → `HandoffManager.create_handoff()`
   - `handoffs.get(handoff_id)` → `HandoffManager.get_handoff_status()`
   - `handoffs.await(handoff_id, timeout_ms)` → `HandoffManager.await_result()`
   - `handoffs.cancel(handoff_id)` → new method
   - `handoffs.accept(handoff_id)` → `HandoffReceiver.accept()`
   - `handoffs.complete(handoff_id, result_trace_id)` → `HandoffReceiver.complete()`
   - `handoffs.fail(handoff_id, reason)` → `HandoffReceiver.fail()`
   - `handoffs.subscribe(project_id)` → `HandoffReceiver.poll_handoffs()` as generator
3. Add `handoffs.send()` as alias for `create()` + `await()` (matches A2A `message.send`)
4. Export from `__init__.py`

**Output:** `src/contextcore/api/handoffs.py`

---

### Feature 4.1C: Skills API Facade

**Task:** Create a new facade module that exposes A2A-style naming for the Skills API.

**Requirements:**
1. Create `src/contextcore/api/skills.py` with class `SkillsAPI`
2. Methods (map to existing SkillCapabilityEmitter/Querier):
   - `skills.emit(manifest, capabilities)` → `SkillCapabilityEmitter.emit_skill_with_capabilities()`
   - `skills.query(trigger, category, budget)` → `SkillCapabilityQuerier` methods
   - `skills.get(skill_id)` → fetch single skill manifest
   - `skills.list()` → list all registered skills
   - `capabilities.emit(skill_id, capability)` → `emit_capability()`
   - `capabilities.invoke(skill_id, capability_id, inputs)` → `emit_invoked()`
   - `capabilities.complete(skill_id, capability_id, outputs)` → `emit_succeeded()`
   - `capabilities.fail(skill_id, capability_id, error)` → `emit_failed()`
3. Export from `__init__.py`

**Output:** `src/contextcore/api/skills.py`

---

### Feature 4.1D: API Package Init

**Task:** Create the unified API package that exports all facades.

**Requirements:**
1. Create `src/contextcore/api/__init__.py`
2. Export all API classes: `InsightsAPI`, `HandoffsAPI`, `SkillsAPI`
3. Create convenience factory functions:
   - `create_insights_api(project_id, agent_id)` → returns configured `InsightsAPI`
   - `create_handoffs_api(project_id, agent_id)` → returns configured `HandoffsAPI`
   - `create_skills_api(agent_id)` → returns configured `SkillsAPI`
4. Create unified `ContextCoreAPI` class that combines all three
5. Example usage in docstring:
   ```python
   from contextcore.api import ContextCoreAPI

   api = ContextCoreAPI(project_id="checkout", agent_id="claude-code")
   api.insights.emit(type="decision", summary="...", confidence=0.9)
   api.handoffs.create(to_agent="o11y", capability_id="investigate", ...)
   api.skills.query(trigger="format")
   ```

**Output:** `src/contextcore/api/__init__.py`

---

## Feature 4.2: State Model Enhancement

Enhance HandoffStatus and add new state-related models aligned with A2A TaskState.

### Feature 4.2A: Enhanced HandoffStatus

**Task:** Extend HandoffStatus enum with A2A-aligned states.

**Requirements:**
1. Update `src/contextcore/agent/handoff.py` HandoffStatus enum:
   ```python
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
   ```
2. Add helper methods:
   - `is_terminal() -> bool` - returns True for COMPLETED, FAILED, TIMEOUT, CANCELLED, REJECTED
   - `is_active() -> bool` - returns True for PENDING, ACCEPTED, IN_PROGRESS, INPUT_REQUIRED
   - `can_transition_to(target: HandoffStatus) -> bool` - validates state transitions
3. Define valid state transitions:
   - PENDING → ACCEPTED, REJECTED, CANCELLED
   - ACCEPTED → IN_PROGRESS, CANCELLED
   - IN_PROGRESS → INPUT_REQUIRED, COMPLETED, FAILED, CANCELLED
   - INPUT_REQUIRED → IN_PROGRESS, COMPLETED, FAILED, CANCELLED
4. Update HandoffManager and HandoffReceiver to support new states

**Output:** Updated `src/contextcore/agent/handoff.py`

---

### Feature 4.2B: State Transition Events

**Task:** Create state transition event model for tracking handoff lifecycle.

**Requirements:**
1. Create `src/contextcore/agent/events.py` with:
   ```python
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
   ```
2. Create `HandoffEventEmitter` class:
   - `emit_status_update(handoff_id, from_status, to_status)` - emits OTel span event
   - `emit_input_required(handoff_id, question, options)` - emits input request
   - `emit_artifact_added(handoff_id, artifact_id, artifact_type)` - emits artifact event
3. Integrate with existing HandoffManager to emit events on state changes

**Output:** `src/contextcore/agent/events.py`

---

### Feature 4.2C: Input Request Model

**Task:** Create model for INPUT_REQUIRED state requests.

**Requirements:**
1. Create `src/contextcore/agent/input_request.py` with:
   ```python
   @dataclass
   class InputOption:
       value: str
       label: str
       description: str | None = None

   @dataclass
   class InputRequest:
       request_id: str
       handoff_id: str
       question: str
       input_type: InputType  # text, choice, multi_choice, confirmation
       options: list[InputOption] | None = None
       default_value: str | None = None
       required: bool = True
       timeout_ms: int = 300000
       created_at: datetime

   class InputType(str, Enum):
       TEXT = "text"
       CHOICE = "choice"
       MULTI_CHOICE = "multi_choice"
       CONFIRMATION = "confirmation"
       FILE = "file"
   ```
2. Add methods to HandoffReceiver:
   - `request_input(handoff_id, question, input_type, options)` - creates InputRequest, sets status to INPUT_REQUIRED
   - `provide_input(handoff_id, request_id, value)` - provides response, resumes handoff
3. Store InputRequests in storage backend

**Output:** `src/contextcore/agent/input_request.py`

---

## Feature 4.3: AgentCard & Discovery

Implement A2A-compatible agent discovery with ContextCore extensions.

### Feature 4.3A: AgentCard Model

**Task:** Create AgentCard model compatible with A2A specification.

**Requirements:**
1. Create `src/contextcore/discovery/agent_card.py` with:
   ```python
   @dataclass
   class AgentCapabilities:
       streaming: bool = False
       push_notifications: bool = False
       insights: bool = True           # CC extension
       handoffs: bool = True           # CC extension
       skills: bool = True             # CC extension
       otel_native: bool = True        # CC extension

   @dataclass
   class SkillDescriptor:
       id: str
       name: str
       description: str
       tags: list[str]
       examples: list[str] = field(default_factory=list)
       input_modes: list[str] = field(default_factory=lambda: ["application/json"])
       output_modes: list[str] = field(default_factory=lambda: ["application/json"])

   @dataclass
   class AuthConfig:
       schemes: list[str]  # Bearer, Basic, ApiKey
       credentials_url: str | None = None

   @dataclass
   class AgentCard:
       agent_id: str
       name: str
       description: str
       url: str
       version: str
       capabilities: AgentCapabilities
       skills: list[SkillDescriptor]
       authentication: AuthConfig | None = None
       # A2A fields
       default_input_modes: list[str] = field(default_factory=lambda: ["application/json"])
       default_output_modes: list[str] = field(default_factory=lambda: ["application/json"])
       documentation_url: str | None = None
       provider: dict[str, str] | None = None
       # ContextCore extensions
       tempo_url: str | None = None
       traceql_prefix: str | None = None
       project_refs: list[str] = field(default_factory=list)

       def to_a2a_json(self) -> dict:
           """Export as A2A-compatible JSON."""
           ...

       def to_contextcore_json(self) -> dict:
           """Export with ContextCore extensions."""
           ...

       @classmethod
       def from_skill_manifest(cls, manifest: SkillManifest, ...) -> "AgentCard":
           """Create AgentCard from existing SkillManifest."""
           ...
   ```

**Output:** `src/contextcore/discovery/agent_card.py`

---

### Feature 4.3B: Discovery Endpoint

**Task:** Create well-known discovery endpoint handler.

**Requirements:**
1. Create `src/contextcore/discovery/endpoint.py` with:
   ```python
   class DiscoveryEndpoint:
       """Serves .well-known/contextcore.json and .well-known/agent.json"""

       def __init__(self, agent_card: AgentCard):
           self.agent_card = agent_card

       def get_contextcore_json(self) -> dict:
           """Returns full ContextCore discovery document."""
           return {
               "version": "1.0",
               "protocol": "contextcore",
               "agent": self.agent_card.to_contextcore_json(),
               "discovery": {
                   "tempo_url": self.agent_card.tempo_url,
                   "traceql_prefix": self.agent_card.traceql_prefix,
               },
               "endpoints": {
                   "insights": "/api/v1/insights",
                   "handoffs": "/api/v1/handoffs",
                   "skills": "/api/v1/skills",
               }
           }

       def get_a2a_agent_json(self) -> dict:
           """Returns A2A-compatible agent.json."""
           return self.agent_card.to_a2a_json()
   ```
2. Create Flask/FastAPI blueprint for serving endpoints (optional integration)
3. Create CLI command: `contextcore discovery serve --port 8080`

**Output:** `src/contextcore/discovery/endpoint.py`

---

### Feature 4.3C: Discovery Client

**Task:** Create client for discovering remote agents.

**Requirements:**
1. Create `src/contextcore/discovery/client.py` with:
   ```python
   class DiscoveryClient:
       """Discover and cache remote agent capabilities."""

       def __init__(self, cache_ttl_seconds: int = 300):
           self._cache: dict[str, tuple[AgentCard, datetime]] = {}
           self.cache_ttl = cache_ttl_seconds

       def discover(self, base_url: str) -> AgentCard:
           """Fetch AgentCard from remote agent."""
           # Try ContextCore endpoint first
           # Fall back to A2A endpoint
           # Parse and cache result
           ...

       def discover_from_tempo(self, agent_id: str, tempo_url: str) -> AgentCard | None:
           """Discover agent from Tempo spans (ContextCore-native)."""
           # Query: { agent.id = "{agent_id}" && name =~ "skill:.*" }
           # Build AgentCard from skill spans
           ...

       def list_known_agents(self) -> list[AgentCard]:
           """Return all cached agents."""
           ...

       def invalidate(self, agent_id: str) -> None:
           """Remove agent from cache."""
           ...
   ```
2. Support both HTTP discovery and Tempo-based discovery

**Output:** `src/contextcore/discovery/client.py`

---

### Feature 4.3D: Discovery Package Init

**Task:** Create discovery package with CLI integration.

**Requirements:**
1. Create `src/contextcore/discovery/__init__.py` exporting:
   - `AgentCard`, `AgentCapabilities`, `SkillDescriptor`, `AuthConfig`
   - `DiscoveryEndpoint`, `DiscoveryClient`
2. Create `src/contextcore/cli/discovery.py` with Click commands:
   - `contextcore discovery card --agent-id X --output agent.json` - generate AgentCard
   - `contextcore discovery serve --port 8080` - serve discovery endpoints
   - `contextcore discovery fetch --url https://agent.example.com` - fetch remote AgentCard
   - `contextcore discovery list` - list agents from Tempo
3. Register with main CLI

**Output:** `src/contextcore/discovery/__init__.py`, `src/contextcore/cli/discovery.py`

---

## Feature 4.4: Part Model Unification

Unify Evidence and content types into A2A-compatible Part model.

### Feature 4.4A: Unified Part Model

**Task:** Create unified Part model that supports both A2A and ContextCore content types.

**Requirements:**
1. Create `src/contextcore/models/part.py` with:
   ```python
   class PartType(str, Enum):
       # A2A-compatible types
       TEXT = "text"
       FILE = "file"
       DATA = "data"
       JSON = "json"
       FORM = "form"
       # ContextCore observability types
       TRACE = "trace"
       LOG_QUERY = "log_query"
       METRIC_QUERY = "metric_query"
       SPAN = "span"
       # ContextCore artifact types
       COMMIT = "commit"
       PR = "pr"
       ADR = "adr"
       DOC = "doc"
       CAPABILITY = "capability"
       INSIGHT = "insight"

   @dataclass
   class Part:
       """Unified content part (A2A-compatible with CC extensions)."""
       type: PartType

       # Text content
       text: str | None = None

       # File content
       file_uri: str | None = None
       mime_type: str | None = None

       # Structured data
       data: dict[str, Any] | None = None

       # ContextCore observability
       trace_id: str | None = None
       span_id: str | None = None
       query: str | None = None  # TraceQL, LogQL, PromQL

       # Reference
       ref: str | None = None
       description: str | None = None

       # Token budget (CC extension)
       tokens: int | None = None

       # Timestamp
       timestamp: datetime | None = None

       def to_a2a_dict(self) -> dict:
           """Convert to A2A Part format."""
           ...

       def to_evidence(self) -> "Evidence":
           """Convert to legacy Evidence format."""
           ...

       @classmethod
       def from_evidence(cls, evidence: "Evidence") -> "Part":
           """Create Part from legacy Evidence."""
           ...

       @classmethod
       def text_part(cls, text: str) -> "Part":
           """Factory for text part."""
           return cls(type=PartType.TEXT, text=text)

       @classmethod
       def trace_part(cls, trace_id: str, description: str = None) -> "Part":
           """Factory for trace reference part."""
           return cls(type=PartType.TRACE, trace_id=trace_id, description=description)
   ```

**Output:** `src/contextcore/models/part.py`

---

### Feature 4.4B: Message Model

**Task:** Create A2A-compatible Message model for handoff communication.

**Requirements:**
1. Create `src/contextcore/models/message.py` with:
   ```python
   class MessageRole(str, Enum):
       USER = "user"      # Client/caller
       AGENT = "agent"    # Remote agent
       SYSTEM = "system"  # System-generated (CC extension)

   @dataclass
   class Message:
       """A2A-compatible message with ContextCore extensions."""
       message_id: str
       role: MessageRole
       parts: list[Part]
       timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
       # ContextCore extensions
       agent_id: str | None = None
       session_id: str | None = None
       metadata: dict[str, Any] = field(default_factory=dict)

       def to_a2a_dict(self) -> dict:
           """Convert to A2A Message format."""
           return {
               "messageId": self.message_id,
               "role": self.role.value,
               "parts": [p.to_a2a_dict() for p in self.parts],
               "timestamp": self.timestamp.isoformat(),
           }

       @classmethod
       def from_text(cls, text: str, role: MessageRole = MessageRole.USER) -> "Message":
           """Create message from plain text."""
           return cls(
               message_id=f"msg-{uuid.uuid4().hex[:12]}",
               role=role,
               parts=[Part.text_part(text)],
           )
   ```
2. Update Handoff model to include `messages: list[Message]` field

**Output:** `src/contextcore/models/message.py`

---

### Feature 4.4C: Artifact Model

**Task:** Create A2A-compatible Artifact model for handoff outputs.

**Requirements:**
1. Create `src/contextcore/models/artifact.py` with:
   ```python
   @dataclass
   class Artifact:
       """A2A-compatible artifact with ContextCore extensions."""
       artifact_id: str
       parts: list[Part]
       media_type: str = "application/json"
       index: int = 0
       append: bool = False
       last_chunk: bool = True
       # ContextCore extensions
       trace_id: str | None = None  # Link to OTel trace
       metadata: dict[str, Any] = field(default_factory=dict)

       def to_a2a_dict(self) -> dict:
           """Convert to A2A Artifact format."""
           ...

       @classmethod
       def from_insight(cls, insight: "Insight") -> "Artifact":
           """Create artifact from Insight."""
           ...

       @classmethod
       def from_json(cls, data: dict, artifact_id: str = None) -> "Artifact":
           """Create artifact from JSON data."""
           ...
   ```
2. Update Handoff model to include `artifacts: list[Artifact]` field

**Output:** `src/contextcore/models/artifact.py`

---

### Feature 4.4D: Models Package Init

**Task:** Create models package with backward compatibility.

**Requirements:**
1. Create `src/contextcore/models/__init__.py` exporting:
   - `Part`, `PartType`
   - `Message`, `MessageRole`
   - `Artifact`
   - Legacy `Evidence` (re-exported for backward compatibility)
2. Update `src/contextcore/agent/insights.py` to use `Part` internally
3. Add `Evidence` as alias: `Evidence = Part` with deprecation warning
4. Update existing code to use new models where appropriate

**Output:** `src/contextcore/models/__init__.py`

---

## Feature 4.5: A2A Protocol Adapter

Create adapter layer for bidirectional A2A protocol support.

### Feature 4.5A: A2A Task Adapter

**Task:** Create adapter to translate between A2A Task and ContextCore Handoff.

**Requirements:**
1. Create `src/contextcore/a2a/task_adapter.py` with:
   ```python
   class TaskAdapter:
       """Bidirectional translation between A2A Task and CC Handoff."""

       @staticmethod
       def handoff_to_task(handoff: Handoff) -> dict:
           """Convert ContextCore Handoff to A2A Task JSON."""
           return {
               "taskId": handoff.id,
               "contextId": handoff.project_id,
               "status": TaskAdapter._status_to_task_state(handoff.status),
               "messages": [m.to_a2a_dict() for m in handoff.messages],
               "artifacts": [a.to_a2a_dict() for a in handoff.artifacts],
               "createdTime": handoff.created_at.isoformat(),
               "updatedTime": datetime.now(timezone.utc).isoformat(),
           }

       @staticmethod
       def task_to_handoff(task: dict, from_agent: str, to_agent: str) -> Handoff:
           """Convert A2A Task JSON to ContextCore Handoff."""
           ...

       @staticmethod
       def _status_to_task_state(status: HandoffStatus) -> str:
           """Map HandoffStatus to A2A TaskState."""
           mapping = {
               HandoffStatus.PENDING: "PENDING",
               HandoffStatus.ACCEPTED: "WORKING",
               HandoffStatus.IN_PROGRESS: "WORKING",
               HandoffStatus.INPUT_REQUIRED: "INPUT_REQUIRED",
               HandoffStatus.COMPLETED: "COMPLETED",
               HandoffStatus.FAILED: "FAILED",
               HandoffStatus.TIMEOUT: "FAILED",
               HandoffStatus.CANCELLED: "CANCELLED",
               HandoffStatus.REJECTED: "REJECTED",
           }
           return mapping.get(status, "PENDING")

       @staticmethod
       def _task_state_to_status(state: str) -> HandoffStatus:
           """Map A2A TaskState to HandoffStatus."""
           ...
   ```

**Output:** `src/contextcore/a2a/task_adapter.py`

---

### Feature 4.5B: A2A Message Handler

**Task:** Create JSON-RPC message handler for A2A protocol methods.

**Requirements:**
1. Create `src/contextcore/a2a/message_handler.py` with:
   ```python
   class A2AMessageHandler:
       """Handle A2A JSON-RPC messages."""

       def __init__(self, handoffs_api: HandoffsAPI, skills_api: SkillsAPI):
           self.handoffs = handoffs_api
           self.skills = skills_api
           self._methods = {
               "message.send": self._handle_message_send,
               "tasks.get": self._handle_tasks_get,
               "tasks.list": self._handle_tasks_list,
               "tasks.cancel": self._handle_tasks_cancel,
               "agent.getExtendedAgentCard": self._handle_get_agent_card,
           }

       def handle(self, request: dict) -> dict:
           """Handle JSON-RPC 2.0 request."""
           method = request.get("method")
           params = request.get("params", {})
           request_id = request.get("id")

           if method not in self._methods:
               return self._error_response(request_id, -32601, "Method not found")

           try:
               result = self._methods[method](params)
               return {"jsonrpc": "2.0", "result": result, "id": request_id}
           except Exception as e:
               return self._error_response(request_id, -32000, str(e))

       def _handle_message_send(self, params: dict) -> dict:
           """Handle message.send - creates handoff and waits for result."""
           ...

       def _handle_tasks_get(self, params: dict) -> dict:
           """Handle tasks.get - returns task/handoff status."""
           ...
   ```

**Output:** `src/contextcore/a2a/message_handler.py`

---

### Feature 4.5C: A2A Server

**Task:** Create HTTP server that speaks A2A protocol.

**Requirements:**
1. Create `src/contextcore/a2a/server.py` with:
   ```python
   class A2AServer:
       """HTTP server implementing A2A protocol endpoints."""

       def __init__(
           self,
           agent_card: AgentCard,
           handoffs_api: HandoffsAPI,
           skills_api: SkillsAPI,
           host: str = "0.0.0.0",
           port: int = 8080,
       ):
           self.agent_card = agent_card
           self.handler = A2AMessageHandler(handoffs_api, skills_api)
           self.discovery = DiscoveryEndpoint(agent_card)
           self.host = host
           self.port = port

       def create_app(self):
           """Create WSGI/ASGI application."""
           # Using Flask or FastAPI
           # Routes:
           # GET /.well-known/agent.json → A2A agent card
           # GET /.well-known/contextcore.json → CC discovery
           # POST /a2a → JSON-RPC handler
           # GET /a2a/sse/{task_id} → SSE streaming (optional)
           ...

       def run(self):
           """Start the server."""
           ...
   ```
2. Create CLI command: `contextcore a2a serve --port 8080`

**Output:** `src/contextcore/a2a/server.py`

---

### Feature 4.5D: A2A Client

**Task:** Create client for communicating with A2A-compatible agents.

**Requirements:**
1. Create `src/contextcore/a2a/client.py` with:
   ```python
   class A2AClient:
       """Client for communicating with A2A-compatible agents."""

       def __init__(self, base_url: str, auth: AuthConfig | None = None):
           self.base_url = base_url.rstrip("/")
           self.auth = auth
           self._http = httpx.Client()

       def send_message(
           self,
           message: Message,
           context_id: str | None = None,
       ) -> dict:
           """Send message to remote agent (message.send)."""
           request = {
               "jsonrpc": "2.0",
               "method": "message.send",
               "params": {
                   "message": message.to_a2a_dict(),
                   "contextId": context_id,
               },
               "id": str(uuid.uuid4()),
           }
           response = self._http.post(f"{self.base_url}/a2a", json=request)
           return response.json()

       def get_task(self, task_id: str) -> dict:
           """Get task status (tasks.get)."""
           ...

       def cancel_task(self, task_id: str) -> dict:
           """Cancel task (tasks.cancel)."""
           ...

       def get_agent_card(self) -> AgentCard:
           """Fetch agent card from .well-known/agent.json."""
           ...

       # Convenience method that converts A2A response to CC Handoff
       def send_and_convert(self, message: Message) -> Handoff:
           """Send message and convert response to ContextCore Handoff."""
           ...
   ```

**Output:** `src/contextcore/a2a/client.py`

---

### Feature 4.5E: A2A Package Init

**Task:** Create A2A package with full exports.

**Requirements:**
1. Create `src/contextcore/a2a/__init__.py` exporting:
   - `TaskAdapter`
   - `A2AMessageHandler`
   - `A2AServer`
   - `A2AClient`
2. Create `src/contextcore/cli/a2a.py` with Click commands:
   - `contextcore a2a serve --port 8080 --agent-id X` - start A2A server
   - `contextcore a2a send --url URL --message "text"` - send message to remote agent
   - `contextcore a2a status --url URL --task-id X` - get task status
3. Register with main CLI

**Output:** `src/contextcore/a2a/__init__.py`, `src/contextcore/cli/a2a.py`

---

## Execution Plan

### Phase 4.1: Naming Conventions (4 features)
```bash
python3 scripts/lead_contractor/cli.py run naming
```

### Phase 4.2: State Model (3 features)
```bash
python3 scripts/lead_contractor/cli.py run state
```

### Phase 4.3: Discovery (4 features)
```bash
python3 scripts/lead_contractor/cli.py run discovery
```

### Phase 4.4: Part Model (4 features)
```bash
python3 scripts/lead_contractor/cli.py run parts
```

### Phase 4.5: A2A Adapter (5 features)
```bash
python3 scripts/lead_contractor/cli.py run a2a
```

---

## Success Criteria

1. **Naming Migration**: All APIs accessible via `resource.action` pattern
2. **State Enhancement**: INPUT_REQUIRED, CANCELLED, REJECTED states working
3. **Discovery**: AgentCard served at `.well-known/contextcore.json`
4. **Part Unification**: Single Part model handles all content types
5. **A2A Interop**: Can send/receive messages with A2A-compatible agents
6. **Backward Compatibility**: Existing code continues to work
7. **OTel Preserved**: All data still stored as OTel spans in Tempo

---

## Dependencies

- Python 3.9+
- httpx (HTTP client)
- Flask or FastAPI (optional, for A2A server)
- Existing ContextCore modules

---

## Risk Mitigation

1. **Breaking Changes**: Use facade pattern, deprecation warnings
2. **Performance**: Cache discovery results, lazy-load adapters
3. **Complexity**: Each feature is self-contained, can be adopted incrementally
