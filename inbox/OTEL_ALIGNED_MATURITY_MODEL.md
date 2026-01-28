# OTel-Aligned Maturity Model for ContextCore

**Status**: Draft (ready for review)
**Reference**: https://opentelemetry.io/docs/specs/otel/versioning-and-stability/
**Created**: 2026-01-28
**Updated**: 2026-01-28

---

## Purpose

Align ContextCore's capability maturity definitions with OpenTelemetry's versioning and stability specification to:
- Set clear expectations for capability consumers (agents, developers)
- Communicate risk appropriately for non-stable capabilities
- Define versioning guarantees that match industry standards
- Establish deprecation and removal policies

---

## Maturity Levels

### Development

**OTel equivalent**: Development

**Definition**:
> A capability in active design or early implementation. Not ready for any external consumption. May be incomplete, broken, or removed without notice.

**Criteria** (any of these):
- Implementation exists but is incomplete
- No tests or failing tests
- No documentation
- No production validation
- API surface actively changing

**Consumer warning**:
> **WARNING**: Do not take production dependencies on Development capabilities. Breaking changes may occur without notice. Capabilities may be removed entirely.

**What this means for ContextCore**:
- Development capabilities may appear in code but should not be used by agents
- No semantic convention guarantees (attribute names may change)
- No CLI support expected
- No dashboard support expected

**Examples**:
- `contextcore.coyote.*` (Wiisagi-ma'iingan) — Multi-agent orchestration (design only)
- `contextcore.fox.*` (Waagosh) — Context enrichment (design only)

---

### Experimental

**OTel equivalent**: Between Development and Stable (OTel uses "Development" broadly; this is a useful intermediate)

**Definition**:
> A capability that is functionally complete and usable, but lacks full production validation or may have API changes pending. Suitable for early adopters and non-critical paths.

**Criteria** (all must be true):
- [x] Implementation complete (core functionality works)
- [x] Basic test coverage exists (happy path tested)
- [x] Under active validation (used by demo generator OR internal testing)
- [ ] API surface may change with deprecation notice

**Consumer guidance**:
> Suitable for early adopters and non-critical paths. Breaking changes possible but will include migration guidance. Minimum 30-day notice for breaking changes.

**Semantic convention stability**:
- Attribute names (`task.*`, `insight.*`) may change with 30-day notice
- Changes will include migration guide
- Dual-emit period required for attribute renames

**What this means for ContextCore**:
- Experimental capabilities can be used by agents with caution
- CLI commands may exist but flags/options may change
- Dashboards may reference these attributes but may need updates
- Documentation exists but may be incomplete

**Examples**:
- `contextcore.handoff.*` — Agent-to-agent delegation
- `contextcore.guidance.*` — Human constraint reading
- `contextcore.code_generation.*` — Generation contracts
- `contextcore.size_estimation.*` — Output size estimation
- `contextcore.rabbit.*` (Waabooz) — Alert automation
- `contextcore.beaver.*` (Amik) — LLM provider abstraction
- `contextcore.squirrel.*` (Ajidamoo) — Skills library
- CLI commands (varying coverage)
- Dashboard provisioning

---

### Stable

**OTel equivalent**: Stable

**Definition**:
> A capability that is production-ready, fully documented, and covered by backward-compatibility guarantees. Safe to depend on for critical paths.

**Criteria** (ALL must be true):

| Criterion | Evidence Required |
|-----------|-------------------|
| **Code complete** | Implementation covers all documented behavior |
| **Test coverage** | Unit tests exist and pass; integration tests for critical paths |
| **Documentation** | API reference exists; usage examples exist; migration guide if upgraded from Experimental |
| **Example exists** | In `/examples/` directory or inline in docs |
| **Production validation** | Demo generator exercises it OR documented external use |

**Versioning guarantees**:

| Guarantee | Commitment |
|-----------|------------|
| API stability | Backward-incompatible changes require major version bump |
| Support period | Minimum 3 months support after deprecation notice |
| Semantic conventions | Attribute names frozen; no breaking changes to stable attributes |
| Deprecation notice | Minimum 30 days before any breaking change |

**What "backward-compatible" means**:
- ✅ Adding new optional parameters
- ✅ Adding new return fields
- ✅ Adding new enum values (if consumers handle unknown values)
- ❌ Removing parameters
- ❌ Changing parameter types
- ❌ Changing return types
- ❌ Renaming attributes without dual-emit period

**What this means for ContextCore**:
- Stable capabilities are safe for agent dependencies
- TrackerAPI methods won't change signature
- InsightEmitter interface frozen
- Semantic conventions (`task.status`, `insight.type`) won't break dashboards
- CLI commands have stable flags

**Examples**:
- `contextcore.task.create` — Start task span
- `contextcore.task.update_status` — Change task status
- `contextcore.task.complete` — End task span
- `contextcore.insight.emit` — Emit insight span
- `contextcore.insight.query` — Query prior insights

---

### Deprecated

**OTel equivalent**: Deprecated

**Definition**:
> A capability marked for removal, with a stable replacement available or removal justified. Receives maintenance but no new features.

**Requirements** (ALL must be true):
- [x] Replacement capability is Stable (if applicable)
- [x] Migration path documented
- [x] Deprecation notice period observed

**Deprecation notice periods**:

| Capability Type | Minimum Notice |
|-----------------|----------------|
| Core API (TaskTracker, InsightEmitter) | 90 days |
| CLI commands | 30 days |
| Semantic conventions (attributes) | 90 days (with dual-emit) |
| Dashboard features | 14 days |
| Expansion pack features | 30 days |

**What deprecated capabilities receive**:
- Same support guarantees as Stable
- Bug fixes for security issues
- No new features
- Warnings in CLI output
- Deprecation badges in documentation

**How deprecation is communicated**:
1. Changelog entry with deprecation notice
2. CLI warning when deprecated capability is used
3. Documentation badge: ![Deprecated](https://img.shields.io/badge/stability-deprecated-orange)
4. Migration guide linked from all deprecation notices

**Examples**:
- None currently
- (Future: `agent.*` attributes when fully migrated to `gen_ai.*`)

---

### Removed

**OTel equivalent**: Removed

**Definition**:
> Capability support has ended. Code deleted or disabled. Using it will fail.

**Requirements**:
- [x] Deprecation period completed
- [x] Major version bump (if removing from public API)
- [x] Removal documented in changelog
- [x] Migration guide remains available

**What this means for ContextCore**:
- Removed capabilities are deleted from codebase
- Import/usage will fail with clear error message
- Semantic conventions removed from documentation
- Dashboards updated to remove references

**Examples**:
- `merge_files_intelligently()` text-based merge — Replaced by AST-based merge in `parts.py`
- (This was internal, not public API, so no formal deprecation was required)

---

## Semantic Convention Stability

ContextCore defines semantic conventions for telemetry attributes. These require special stability treatment because they affect:
- TraceQL queries
- Grafana dashboards
- Agent decision logic
- Cross-system interoperability

### Attribute Categories

| Category | Attributes | Stability |
|----------|------------|-----------|
| **Task** | `task.id`, `task.type`, `task.status`, `task.priority`, `task.title`, `task.assignee`, `task.story_points`, `task.parent_id` | **Stable** |
| **Insight** | `insight.id`, `insight.type`, `insight.confidence`, `insight.summary` | **Stable** |
| **Handoff** | `handoff.id`, `handoff.status`, `handoff.from_agent`, `handoff.to_agent` | Experimental |
| **Agent (legacy)** | `agent.id`, `agent.session_id`, `agent.type` | Deprecated (migrating to `gen_ai.*`) |
| **GenAI (OTel)** | `gen_ai.user`, `gen_ai.request_id`, `gen_ai.operation.name` | Experimental (OTel alignment in progress) |
| **Project** | `project.id`, `project.epic` | **Stable** |

### What "stable semantic conventions" means

Per OTel spec:
> Telemetry fields covered by stability guarantees cannot break analysis tools after schema transformations are applied.

For ContextCore this means:
- Dashboards using `task.status = "in_progress"` won't break
- TraceQL queries using stable attributes will continue to work
- Agents querying `insight.confidence > 0.8` will get consistent results

### Changing stable attributes

If a stable attribute must change:

1. **Dual-emit period**: Emit both old and new attribute for minimum 90 days
2. **Migration tooling**: Provide script or documentation to update queries/dashboards
3. **Dashboard updates**: Update all provisioned dashboards before deprecation ends
4. **Communication**: Changelog, CLI warnings, documentation badges

Example (current): `agent.id` → `gen_ai.user` migration uses `CONTEXTCORE_OTEL_MODE` env var to control dual-emit.

---

## Versioning Scheme

### Version format

```
MAJOR.MINOR.PATCH[-PRERELEASE]

Examples:
1.2.3
2.0.0-beta.1
```

### What triggers each version type

| Version | Trigger | Examples |
|---------|---------|----------|
| **MAJOR** | Backward-incompatible API changes, removed capabilities | Removing `agent.*` attributes, changing TaskTracker signature |
| **MINOR** | New capabilities, new optional parameters, Experimental → Stable promotions | Adding `contextcore.handoff.*`, new CLI command |
| **PATCH** | Bug fixes, security fixes, documentation updates | Fix insight query edge case, update README |

### Pre-release versions

- `-alpha.N`: Development maturity, not for external use
- `-beta.N`: Experimental maturity, early adopter testing
- `-rc.N`: Release candidate, stable barring issues

### Current version

- ContextCore SDK: **0.x.y** (pre-1.0, all APIs are Experimental by default)
- Note: 1.0.0 release will formalize Stable guarantees

---

## Transition Rules

### Development → Experimental

**Requirements**:
- [x] Implementation complete (core functionality)
- [x] Basic tests passing
- [x] Initial documentation exists (at least docstrings)

**Approval**: Self-declaration with evidence documented in PR/commit

**Announcement**: Changelog entry

### Experimental → Stable

**Requirements**:
- [x] All Stable criteria met (see above)
- [x] Minimum 30 days in Experimental
- [x] Used by demo generator OR documented external use
- [x] No open P1/P2 bugs against the capability

**Approval**: Self-declaration with evidence documented; recommend peer review for core APIs

**Announcement**: Changelog entry, documentation update, badge change

### Stable → Deprecated

**Requirements**:
- [x] Replacement is Stable (if applicable) OR removal justified
- [x] Migration guide written
- [x] Deprecation notice published
- [x] CLI warnings implemented (if CLI-facing)

**Approval**: Documented decision with rationale

**Announcement**: Changelog entry, deprecation notice template (see below), documentation badge

### Deprecated → Removed

**Requirements**:
- [x] Deprecation period completed (see notice periods above)
- [x] Major version planned
- [x] Removal announced in changelog
- [x] Migration guide remains accessible

**Approval**: Part of major version release planning

**Announcement**: Changelog entry, major version release notes

---

## Capability Maturity Registry

### Core SDK

| Capability | Current | Target | Evidence | Notes |
|------------|---------|--------|----------|-------|
| `contextcore.task.create` | **Stable** | Stable | tracker.py, tests, examples | Core functionality |
| `contextcore.task.update_status` | **Stable** | Stable | tracker.py, tests | Core functionality |
| `contextcore.task.complete` | **Stable** | Stable | tracker.py, tests | Core functionality |
| `contextcore.task.block` | **Stable** | Stable | tracker.py, tests | Core functionality |
| `contextcore.sprint.start` | Experimental | Stable | tracker.py, limited tests | Needs more validation |
| `contextcore.sprint.end` | Experimental | Stable | tracker.py, limited tests | Needs more validation |
| `contextcore.insight.emit` | **Stable** | Stable | insights.py, tests, examples | Core agent functionality |
| `contextcore.insight.query` | **Stable** | Stable | insights.py, tests | Core agent functionality |
| `contextcore.handoff.initiate` | Experimental | Experimental | handoff.py, tests | Active development |
| `contextcore.handoff.receive` | Experimental | Experimental | handoff.py, tests | Active development |
| `contextcore.guidance.read_constraints` | Experimental | Experimental | guidance.py | Limited docs |
| `contextcore.guidance.check_path` | Experimental | Experimental | guidance.py | Limited docs |
| `contextcore.code_generation.contract` | Experimental | Experimental | code_generation.py | Recent implementation |
| `contextcore.size_estimation.estimate` | Experimental | Experimental | size_estimation.py | Recent implementation |

### CLI

| Command | Current | Target | Evidence | Notes |
|---------|---------|--------|----------|-------|
| `contextcore task` | Experimental | Stable | task.py | Needs flag stability review |
| `contextcore sprint` | Experimental | Experimental | sprint.py | Limited testing |
| `contextcore insight` | Experimental | Stable | insight.py | Core functionality |
| `contextcore install` | Experimental | Stable | install.py | Self-monitoring |
| `contextcore dashboards` | Experimental | Stable | dashboards.py | 11 dashboards provisioned |
| `contextcore demo` | Experimental | Experimental | demo.py | Internal tooling |

### Expansion Packs

| Pack | Current | Target | Evidence | Notes |
|------|---------|--------|----------|-------|
| Rabbit (Waabooz) | Experimental | Experimental | contextcore-rabbit/ | Alert automation |
| Beaver (Amik) | Experimental | Experimental | contextcore-beaver/ | LLM provider |
| Squirrel (Ajidamoo) | Experimental | Experimental | contextcore-squirrel/ | Skills library |
| Coyote (Wiisagi-ma'iingan) | Development | Experimental | Design docs only | Multi-agent orchestration |
| Fox (Waagosh) | Development | Experimental | Design docs only | Context enrichment |
| Owl (Gookooko'oo) | Experimental | Experimental | contextcore-owl/ | Internal Grafana plugins |

---

## Communication Templates

### Deprecation Notice Template

```markdown
## Deprecation Notice: [CAPABILITY_NAME]

**Deprecated in**: v[X.Y.Z]
**Removal planned**: v[X+1.0.0] (estimated [DATE])
**Replacement**: [NEW_CAPABILITY_NAME] (if applicable)

### What's changing
[Description of what's being deprecated and why]

### Migration path
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Timeline
- [DATE]: Deprecation notice (this announcement)
- [DATE]: CLI warnings enabled
- [DATE]: Removal in next major version

### Example migration

Before:
```python
[old code]
```

After:
```python
[new code]
```

### Questions?
Open an issue: [repository URL]
```

### Stability Badge Template

For documentation:
```markdown
![Stability: Development](https://img.shields.io/badge/stability-development-red)
![Stability: Experimental](https://img.shields.io/badge/stability-experimental-yellow)
![Stability: Stable](https://img.shields.io/badge/stability-stable-green)
![Stability: Deprecated](https://img.shields.io/badge/stability-deprecated-orange)
```

### CLI Warning Template

```
⚠️  WARNING: 'contextcore [command]' is deprecated and will be removed in v2.0.0.
    Use 'contextcore [new-command]' instead.
    Migration guide: https://docs.contextcore.io/migration/[capability]
```

---

## Open Questions (Resolved)

| Question | Resolution | Rationale |
|----------|------------|-----------|
| Support period? | 3 months for deprecated capabilities | Personal project; shorter than enterprise OTel (1-3 years) but sufficient for migration |
| Experimental duration? | Minimum 30 days before Stable promotion | Allows time for feedback and issue discovery |
| Approval process? | Self-declaration with documented evidence | Personal project; formal review recommended for core APIs |
| Semantic convention ownership? | Project maintainer | Single owner simplifies decisions |
| Expansion pack versioning? | Independent from core | Different release cycles; `contextcore-rabbit` can be 1.0 while core is 0.x |

---

## References

- [OTel Versioning and Stability](https://opentelemetry.io/docs/specs/otel/versioning-and-stability/)
- [OTel Semantic Conventions Stability](https://opentelemetry.io/docs/specs/otel/document-status/)
- [SemVer Specification](https://semver.org/)
- ContextCore `.contextcore.yaml` (risk definitions)
- ContextCore `docs/semantic-conventions.md` (attribute definitions)
- ContextCore `inbox/CAPABILITY_INDEX_PREPARATION.md` (maturity criteria)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-28 | Initial outline created |
| 2026-01-28 | Filled TODOs with concrete values based on capability index preparation work |
