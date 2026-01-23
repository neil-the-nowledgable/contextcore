---
description: Show active project risks sorted by priority
allowed-tools: Read
---

# Show Project Risks

Read `.contextcore.yaml` and display all active risks sorted by priority.

## Instructions

1. Read the `.contextcore.yaml` file
2. Extract all risks from the `business.risks` section
3. Group and sort by priority: P1 > P2 > P3 > P4
4. For each risk show:
   - Priority badge
   - Risk description
   - Mitigation strategy
   - Affected scope/files (if specified)

## Output Format

```
## P1 - Critical Risks
- [Risk description]
  Mitigation: [strategy]
  Scope: [affected areas]

## P2 - High Priority Risks
...
```

If working on files in a risk's scope, highlight that risk prominently.
