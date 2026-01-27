# Feature: BLC-008 - Add Insight Emission for Workflow Decisions

## Overview
Emit insights to Tempo when the Prime Contractor makes workflow decisions (feature selection, integration outcomes, checkpoint results).

## Target Files
- `scripts/prime_contractor/workflow.py` (modify)

## Requirements

### Insights to Emit
1. **workflow_started** - When workflow begins
2. **feature_selected** - When a feature is picked for integration
3. **integration_success** - When feature passes checkpoints
4. **integration_failed** - When feature fails checkpoints
5. **workflow_completed** - When workflow finishes

### Implementation
```python
from contextcore.agent.insights import InsightEmitter

class PrimeContractorWorkflow:
    def __init__(self, ...):
        self.insight_emitter = InsightEmitter(
            project_id="prime-contractor",
            agent_id="beaver"
        )

    def run(self, ...):
        self.insight_emitter.emit_decision(
            summary=f"Starting workflow with {len(features)} features",
            confidence=1.0,
            context={"mode": "live" if not self.dry_run else "dry_run"}
        )
        # ... existing logic ...
```

### Insight Schema
```python
{
    "type": "decision",
    "summary": "string",
    "confidence": float,
    "context": {
        "feature_id": "string",
        "outcome": "success" | "failed",
        "checkpoint_results": {...}
    }
}
```

## Acceptance Criteria
- [x] InsightEmitter initialized in workflow
- [x] Emits insight on workflow start
- [x] Emits insight for each feature outcome
- [x] Emits summary insight on completion
- [ ] Insights visible in Tempo traces (requires OTel setup)

## Dependencies
- `contextcore.agent.insights.InsightEmitter`

## Size Estimate
~40 lines of code
