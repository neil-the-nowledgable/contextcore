# Feature: BLC-006 - Add Workflow History Panel

## Overview
Add a Grafana table panel to display completed workflow runs with task details, duration, cost, and outcome.

## Target Files
- `grafana/provisioning/dashboards/rabbit/workflow.json` (modify)

## Requirements

### Panel Configuration
```json
{
  "title": "Workflow History",
  "type": "table",
  "targets": [
    {
      "datasource": "Tempo",
      "queryType": "traceql",
      "query": "{resource.service.name=\"lead-contractor\" && name=\"workflow\"} | select(span.attributes.task.title, duration, span.attributes.contextcore.cost.usd, status)"
    }
  ],
  "transformations": [
    {
      "id": "organize",
      "options": {
        "renameByName": {
          "span.attributes.task.title": "Task",
          "duration": "Duration",
          "span.attributes.contextcore.cost.usd": "Cost ($)",
          "status": "Outcome"
        }
      }
    }
  ],
  "fieldConfig": {
    "overrides": [
      {
        "matcher": {"id": "byName", "options": "Cost ($)"},
        "properties": [{"id": "unit", "value": "currencyUSD"}]
      },
      {
        "matcher": {"id": "byName", "options": "Duration"},
        "properties": [{"id": "unit", "value": "s"}]
      }
    ]
  }
}
```

### Columns
1. **Task** - Task title/description
2. **Started** - Timestamp
3. **Duration** - Total time
4. **Cost ($)** - LLM API cost
5. **Outcome** - Success/Failed badge

## Acceptance Criteria
- [ ] Shows last 20 workflow runs
- [ ] Sortable by any column
- [ ] Cost formatted as currency
- [ ] Duration formatted as human-readable time
- [ ] Clickable row links to trace in Tempo

## Dependencies
- BLC-003 (history endpoint for data)
- BLC-009 (cost tracking attributes)

## Size Estimate
~80 lines of JSON config

