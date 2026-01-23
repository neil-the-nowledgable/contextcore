---
description: Display project context, risks, and requirements from .contextcore.yaml
allowed-tools: Read, Grep
---

# Project Context Query

Read and analyze the project's `.contextcore.yaml` file to provide a comprehensive summary.

## Instructions

1. Read the `.contextcore.yaml` file from the project root
2. Parse and present the following information:

### Project Overview
- Project ID and name
- Business criticality level
- Project owner/team

### Risk Matrix
For each risk, show:
- Priority level (P1 = critical, P2 = high, P3 = medium, P4 = low)
- Risk description
- Mitigation strategy
- Affected scope/components (if specified)

### SLO Requirements
- Availability targets
- Latency requirements (P50, P99)
- Throughput expectations
- Error budget

### Design Documentation
- Link to architecture docs
- Semantic conventions
- API contracts

### Recommendations
Based on the context, provide:
- Key considerations for current work
- Risk areas to be careful with
- Relevant documentation to review

## Output Format

Present the information in a clear, structured format that helps developers understand:
1. What this project does and why it matters
2. What could go wrong (risks)
3. What success looks like (SLOs)
4. Where to find more information
