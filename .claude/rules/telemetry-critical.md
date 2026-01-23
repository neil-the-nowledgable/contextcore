---
globs:
  - "src/contextcore/tracker.py"
  - "src/contextcore/state.py"
  - "src/contextcore/metrics.py"
  - "src/contextcore/detector.py"
---

# Telemetry Critical Path Rules

These files are on the critical path for OTLP export and task tracking.

## Risk Awareness

Before modifying these files, check `.contextcore.yaml` for active P1/P2 risks related to:
- OTLP exporter reliability
- Span state persistence
- Task lifecycle management

## Requirements

1. **Graceful Degradation**: All OTLP operations must handle failures without blocking task tracking
2. **State Persistence**: Ensure in-flight spans can be recovered after restart
3. **Thread Safety**: Consider concurrent access patterns in task operations

## Testing Requirements

- Add unit tests for failure scenarios
- Mock OTLP exporter in tests (never hit real endpoints)
- Test graceful shutdown behavior
- Verify state recovery after simulated failures

## Code Review Checklist

- [ ] Error handling doesn't swallow exceptions silently
- [ ] Timeouts configured for all network operations
- [ ] Fallback behavior documented
- [ ] Metrics emitted for failure conditions
