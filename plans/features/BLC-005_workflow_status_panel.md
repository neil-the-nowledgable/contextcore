# Feature: BLC-005 - Add Workflow Status Panel

## Overview
Add a Grafana panel to display active workflow progress with current phase, iteration count, and elapsed time.

## Target Files
- `grafana/provisioning/dashboards/rabbit/workflow.json` (modify)

## Requirements

### Panel Configuration
```json
{
  "title": "Active Workflow Status",
  "type": "stat",
  "targets": [
    {
      "datasource": "Tempo",
      "queryType": "traceql",
      "query": "{resource.service.name=\"lead-contractor\" && status=unset} | select(name, span.attributes.workflow.phase)"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "mappings": [
        {"type": "value", "options": {"spec": {"text": "Spec Creation", "color": "blue"}}},
        {"type": "value", "options": {"draft": {"text": "Drafting", "color": "yellow"}}},
        {"type": "value", "options": {"review": {"text": "Review", "color": "orange"}}},
        {"type": "value", "options": {"integration": {"text": "Integration", "color": "green"}}}
      ]
    }
  }
}
```

### Display Fields
1. **Current Phase** - spec/draft/review/integration
2. **Iteration Count** - How many spec-draft-review cycles
3. **Elapsed Time** - Time since workflow started
4. **Task Title** - What's being worked on

## Acceptance Criteria
- [ ] Panel shows "No active workflows" when idle
- [ ] Phase updates in real-time during workflow
- [ ] Iteration count increments on review rejections
- [ ] Elapsed time updates every 5 seconds

## Dependencies
- BLC-002 (status endpoint for fallback data)

## Size Estimate
~60 lines of JSON config

