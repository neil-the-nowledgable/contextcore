# Feature: BLC-004 - Update Workflow Manager Trigger Panel

## Overview
Update the WorkflowPanel React component to use the correct Rabbit API endpoints instead of the old `/workflow/*` pattern.

## Target Files
- `contextcore-owl/plugins-new/contextcore-workflow-panel/src/components/WorkflowPanel.tsx` (modify)

## Requirements

### Current (Broken)
```typescript
fetch(`${options.apiUrl}/workflow/dry-run`, ...)
fetch(`${options.apiUrl}/workflow/execute`, ...)
fetch(`${options.apiUrl}/workflow/status/${runId}`)
```

### New (Correct)
```typescript
// Dry run
fetch(`${options.apiUrl}/workflow/run`, {
  method: 'POST',
  body: JSON.stringify({ project_id, dry_run: true })
})

// Execute
fetch(`${options.apiUrl}/workflow/run`, {
  method: 'POST',
  body: JSON.stringify({ project_id, dry_run: false })
})

// Status polling
fetch(`${options.apiUrl}/workflow/status/${runId}`)
```

### Implementation
1. Update `handleDryRun()` to POST to `/workflow/run` with `dry_run: true`
2. Update `executeWorkflow()` to POST to `/workflow/run` with `dry_run: false`
3. Keep status polling as GET `/workflow/status/{run_id}`
4. Update response parsing to match new API format

## Acceptance Criteria
- [ ] Dry Run button calls `/workflow/run` with dry_run=true
- [ ] Execute button calls `/workflow/run` with dry_run=false
- [ ] Status polling works with new endpoint
- [ ] Error handling updated for new response format
- [ ] No TypeScript errors

## Dependencies
- BLC-001, BLC-002 (API endpoints must exist)

## Size Estimate
~50 lines changed
