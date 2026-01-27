# Feature: BLC-001 - Add Workflow Run Endpoint to Rabbit API

## Overview
Add a `/workflow/run` endpoint to the Rabbit API server that triggers Prime Contractor workflow execution.

## Target Files
- `contextcore-rabbit/src/contextcore_rabbit/server.py` (modify)

## Requirements

### Endpoint Specification
```
POST /workflow/run
Content-Type: application/json

Request:
{
    "project_id": "string",
    "dry_run": boolean (default: false),
    "max_features": number (optional)
}

Response (200):
{
    "status": "started",
    "run_id": "string",
    "project_id": "string",
    "mode": "dry_run" | "execute"
}

Response (400):
{
    "status": "error",
    "error": "string"
}
```

### Implementation
1. Add new route `/workflow/run` with POST method
2. Parse request body for project_id, dry_run, max_features
3. Call existing `beaver_workflow` action via action_registry
4. Return run_id for status polling

## Acceptance Criteria
- [ ] Endpoint accepts POST requests
- [ ] Validates required project_id field
- [ ] Returns run_id on success
- [ ] Returns 400 on invalid request
- [ ] Integrates with existing beaver_workflow action

## Dependencies
- Existing `beaver_workflow` action in `actions/beaver_workflow.py`

## Size Estimate
~30 lines of code
