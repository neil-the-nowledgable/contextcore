# Feature: BLC-003 - Add Workflow History Endpoint

## Overview
Add a `/workflow/history` endpoint to list completed workflow runs with filtering.

## Target Files
- `contextcore-rabbit/src/contextcore_rabbit/server.py` (modify)
- `contextcore-rabbit/src/contextcore_rabbit/actions/beaver_workflow.py` (modify)

## Requirements

### Endpoint Specification
```
GET /workflow/history?project_id={project_id}&limit={limit}

Query Parameters:
- project_id: string (optional) - filter by project
- limit: number (default: 20) - max results
- status: string (optional) - filter by status

Response (200):
{
    "runs": [
        {
            "run_id": "string",
            "project_id": "string",
            "status": "completed" | "failed",
            "started_at": "ISO8601",
            "completed_at": "ISO8601",
            "duration_seconds": number,
            "steps_completed": number,
            "steps_total": number
        }
    ],
    "total": number
}
```

### Implementation
1. Add new route `/workflow/history` with GET method
2. Add `list_workflow_runs()` function to beaver_workflow.py
3. Filter `_workflow_runs` by project_id and status
4. Sort by started_at descending
5. Apply limit

## Acceptance Criteria
- [ ] Endpoint accepts GET requests with optional filters
- [ ] Returns list of historical runs
- [ ] Filters by project_id when provided
- [ ] Limits results (default 20)
- [ ] Sorted newest first

## Dependencies
- `_workflow_runs` dict in beaver_workflow.py

## Size Estimate
~40 lines of code
