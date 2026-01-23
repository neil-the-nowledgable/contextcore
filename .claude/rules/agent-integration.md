---
globs:
  - "src/contextcore/agent/**"
---

# Agent Integration Rules

These files handle agent-to-agent communication and insight persistence.

## Semantic Conventions

All agent insights must follow the conventions in `docs/agent-semantic-conventions.md`:
- `agent.id` - Unique agent identifier
- `agent.insight.type` - One of: decision, lesson, question, handoff
- `agent.insight.confidence` - Float 0.0-1.0

## Risk Awareness

Check `.contextcore.yaml` for risks related to:
- Insight query latency
- Cross-agent handoff failures
- Personalization data privacy

## Patterns

### Emitting Insights
```python
emitter = InsightEmitter(project_id="proj", agent_id="claude")
emitter.emit_decision(
    summary="Chose X over Y because Z",
    confidence=0.9,
    context={"file": "relevant/file.py"}
)
```

### Querying Prior Context
```python
querier = InsightQuerier()
prior = querier.query(project_id="proj", insight_type="decision", time_range="30d")
```

## Testing

- Mock Tempo backend in tests
- Verify insight schema compliance
- Test query timeout handling
