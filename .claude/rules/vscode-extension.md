---
globs:
  - "extensions/vscode/**"
---

# VSCode Extension Rules

The ContextCore VSCode extension provides project context awareness in the editor.

## Architecture

- **Providers**: Load context from local files, CLI, or Kubernetes
- **Mapping**: Map files to their relevant ProjectContext
- **UI**: Status bar, side panel, and inline decorations
- **Commands**: Refresh, show impact, open dashboard, show risks

## Key Patterns

### Context Loading Priority
1. Local `.contextcore.yaml` file
2. ContextCore CLI (`contextcore context show`)
3. Kubernetes ProjectContext CRD

### Caching
- Cache context with configurable TTL (default 30s)
- Invalidate on file system changes to context files
- Manual refresh via command

## Risk Awareness

Check `.contextcore.yaml` for risks related to:
- Extension activation performance
- Kubernetes API failures
- Cache invalidation edge cases

## Testing

- Test with mock VSCode API
- Verify graceful degradation when context unavailable
- Test all three provider fallback paths
