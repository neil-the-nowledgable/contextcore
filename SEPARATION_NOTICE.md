# Repository Separation Notice

This monorepo has been separated into two repositories as of 2026-02-01.

## New Repositories

| Repository | Purpose | URL |
|-----------|---------|-----|
| **contextcore-spec** | The ContextCore metadata standard (schemas, semantic conventions, protocols, terminology) | https://github.com/contextcore/contextcore-spec |
| **wayfinder** | The Wayfinder reference implementation (Python SDK, CLI, expansion packs, dashboards) | https://github.com/contextcore/wayfinder |

## Historical Reference

The tag `pre-separation-snapshot` marks the last state of this monorepo before separation. Use it to reference any file as it existed prior to the split:

```
git checkout pre-separation-snapshot
```

## Where to Continue

**All new development should happen in the [wayfinder](https://github.com/contextcore/wayfinder) repository.**

- Filing bugs or feature requests? Use the wayfinder repo.
- Proposing changes to the ContextCore standard? Use the contextcore-spec repo.
- Looking for the Python SDK, CLI, or expansion packs? Use the wayfinder repo.
- Looking for schemas, conventions, or protocol definitions? Use the contextcore-spec repo.

## Background

See [ADR-003: Monorepo Separation](https://github.com/contextcore/wayfinder/blob/main/docs/adr/003-monorepo-separation.md) for the full rationale behind this decision.
