# OTel Community Submission Materials

This directory contains ready-to-submit materials for contributing ContextCore patterns to the OpenTelemetry community.

## Submission Checklist

### Before Submitting

- [ ] Complete end-user validation (see `../blueprint-validation-framework.md`)
- [ ] Gather ≥5 interview responses
- [ ] Confirm ≥2 reference architecture commitments
- [ ] Review with ContextCore maintainers

### Community Repository Submissions

| File | Target Repo | Purpose |
|------|-------------|---------|
| `01-community-issue-blueprint-category.md` | `open-telemetry/community` | Project proposal for Project Management Observability Blueprint |
| `02-community-issue-agent-blueprint.md` | `open-telemetry/community` | Project proposal for AI Agent Communication Blueprint |

### Semantic Conventions Submissions

| File | Target Repo | Purpose |
|------|-------------|---------|
| `03-semconv-issue-project-namespace.md` | `open-telemetry/semantic-conventions` | Propose `project.*`, `task.*`, `sprint.*` namespaces |
| `04-semconv-issue-agent-namespace.md` | `open-telemetry/semantic-conventions` | Propose `agent.insight.*` namespace extensions |

## Submission Order

1. **Community proposals first** — Get buy-in on blueprint categories
2. **SemConv proposals second** — After community approval, propose attributes
3. **Blueprint documentation** — Write full blueprints after namespace approval

## How to Submit

### GitHub Issue (Proposals)

1. Go to the target repository
2. Click "New Issue"
3. Copy the content from the relevant `.md` file
4. Add appropriate labels (`project-proposal`, `semantic-conventions`)
5. Tag relevant SIGs (listed in each file)

### Pull Request (Documentation)

After proposals are approved:

1. Fork the target repository
2. Create branch: `blueprint/project-management-observability`
3. Add blueprint documentation following template
4. Reference the approved issue
5. Request review from SIG maintainers

## Supporting Materials

| Document | Purpose |
|----------|---------|
| `../blueprint-reference-architecture.md` | Full blueprint following OTel template |
| `../blueprint-reusable-patterns.md` | Extracted patterns for reuse |
| `../blueprint-implementation-guide.md` | Step-by-step implementation |
| `../blueprint-validation-framework.md` | End-user validation methodology |
| `../migration-guides.md` | Adoption guides for organizations |
| `../../examples/` | Runnable code examples |

## Timeline

| Week | Activity |
|------|----------|
| 1-2 | Complete end-user validation |
| 3 | Submit community proposals (01, 02) |
| 4-5 | Address feedback, iterate |
| 6 | Submit semconv proposals (03, 04) |
| 7-8 | Write full blueprint documentation |
| 9-10 | Community review period |
| 11+ | Merge and announce |

## Contacts

- **OTel End-User SIG**: `#otel-user-sig` on CNCF Slack
- **OTel SemConv WG**: `#otel-semconv-general` on CNCF Slack
- **Gen AI SIG**: `#otel-gen-ai` on CNCF Slack

## Related Links

- [OTel Blueprints Project](https://github.com/open-telemetry/community/blob/main/projects/otel-blueprints.md)
- [SemConv Contributing Guide](https://github.com/open-telemetry/semantic-conventions/blob/main/CONTRIBUTING.md)
- [Community Project Proposal Process](https://github.com/open-telemetry/community/blob/main/project-management.md)
