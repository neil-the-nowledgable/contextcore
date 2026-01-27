# Feature: BLC-002 - Implement Workflow Status Endpoint

## Overview
Add a `/workflow/status/{run_id}` endpoint to query real-time workflow progress.

## Target Files
- `contextcore-rabbit/src/contextcore_rabbit/server.py` (modify)

## Requirements

### Endpoint Specification
```
GET /workflow/status/{run_id}

Response (200):
{
    "run_id": "string",
    "status": "starting" | "running" | "completed" | "failed",
    "project_id": "string",
    "started_at": "ISO8601",
    "completed_at": "ISO8601" | null,
    "duration_seconds": number | null,
    "steps_completed": number,
    "steps_total": number,
    "current_step": "string" | null,
    "error": "string" | null
}

Response (404):
{
    "status": "error",
    "error": "Run not found: {run_id}"
}
```

### Implementation
1. Add new route `/workflow/status/<run_id>` with GET method
2. Call existing `beaver_workflow_status` action
3. Format response with progress details
4. Return 404 if run_id not found

## Acceptance Criteria
- [ ] Endpoint accepts GET requests with run_id path parameter
- [ ] Returns current workflow status
- [ ] Includes progress (steps_completed/steps_total)
- [ ] Returns 404 for unknown run_id
- [ ] Calculates duration_seconds when completed

## Dependencies
- Existing `beaver_workflow_status` action
- `_workflow_runs` dict in beaver_workflow.py

## Size Estimate
~25 lines of code
