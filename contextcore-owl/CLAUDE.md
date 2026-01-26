# CLAUDE.md - contextcore-owl

This file provides guidance to Claude Code for the contextcore-owl expansion pack.

## Project Context

**Package**: contextcore-owl (Gookooko'oo - Owl)
**Purpose**: Unified Grafana plugin package for ContextCore
**Status**: Development

## Tech Stack

- **Plugins**: TypeScript, React, @grafana/ui, @grafana/data, @grafana/runtime
- **Build**: npm workspaces, @grafana/create-plugin
- **Python**: Scaffold script using contextcore-beaver for LLM generation
- **Dev Environment**: Docker Compose with Grafana and mock Rabbit API

## Project Structure

```
contextcore-owl/
├── package.json              # Monorepo root (npm workspaces)
├── pyproject.toml            # Python package
├── plugins/
│   ├── contextcore-chat-panel/
│   ├── contextcore-workflow-panel/
│   └── contextcore-datasource/
├── scripts/
│   └── scaffold_plugin.py
├── grafana/plugins/          # Built plugins
├── docker/
│   ├── docker-compose.yml
│   ├── provisioning/
│   └── mock/
└── docs/
```

## Commands

```bash
# Install dependencies
npm install

# Build all plugins
npm run build

# Development with hot reload
npm run dev

# Scaffold new plugin (requires contextcore-beaver)
python scripts/scaffold_plugin.py --type panel --name my-plugin
```

## Kind Deployment

Plugins are deployed via Kind cluster host mounts. After building:

```bash
# Build plugins (output to grafana/plugins/)
npm run build

# Recreate Kind cluster to pick up new mounts (if first time)
# From /Users/neilyashinsky/Documents/Deploy:
./scripts/create-cluster.sh --delete && ./scripts/create-cluster.sh

# Or just restart Grafana pod to reload plugins
kubectl -n observability rollout restart deployment/grafana

# View Grafana at http://localhost:3000 (admin/admin)
```

**Kind cluster mounts** (defined in `/Users/neilyashinsky/Documents/Deploy/kind-cluster.yaml`):
- Host: `contextcore-owl/grafana/plugins/*` → Container: `/plugins/contextcore/*`
- Grafana deployment uses hostPath volumes to mount from `/plugins/contextcore/*`

## Plugin Development Patterns

### Panel Plugin Structure

```typescript
// module.ts
import { PanelPlugin } from '@grafana/data';
import { MyPanel } from './components/MyPanel';
import { MyPanelOptions } from './types';

export const plugin = new PanelPlugin<MyPanelOptions>(MyPanel)
  .setPanelOptions((builder) => {
    builder.addTextInput({
      path: 'apiUrl',
      name: 'API URL',
      defaultValue: 'http://localhost:8080',
    });
  });
```

### Template Variables

```typescript
import { getTemplateSrv } from '@grafana/runtime';

const templateSrv = getTemplateSrv();
const projectId = templateSrv.replace('${project}');
```

### HTTP Requests

For panel plugins, use direct fetch() with CORS enabled on the API:

```typescript
const response = await fetch(`${options.apiUrl}/endpoint`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data),
});
```

For datasource plugins, use Grafana's route proxy (CORS-free):

```typescript
// plugin.json routes
"routes": [
  { "path": "api/*", "url": "{{ .JsonData.apiUrl }}" }
]

// datasource.ts
const response = await getBackendSrv().fetch({
  url: '/api/plugins/contextcore-datasource/resources/api/endpoint',
  method: 'POST',
});
```

## Key Files

| File | Purpose |
|------|---------|
| `plugins/*/src/module.ts` | Plugin entry point |
| `plugins/*/src/plugin.json` | Plugin manifest |
| `plugins/*/src/types.ts` | TypeScript interfaces |
| `plugins/*/src/components/*.tsx` | React components |

## Testing

```bash
# Run tests
npm test

# Test with mock API
npm run docker:up
# Open http://localhost:3001 (Grafana dev instance)
```

## Ports

| Service | Port | Description |
|---------|------|-------------|
| Grafana (dev) | 3001 | Plugin development |
| Rabbit Mock | 8080 | Mock Rabbit API |

## Related Documentation

- [Grafana Plugin Development](https://grafana.com/developers/plugin-tools/)
- [@grafana/ui Components](https://developers.grafana.com/ui/latest/)
- [ContextCore Expansion Packs](../docs/EXPANSION_PACKS.md)
- [Naming Convention](../docs/NAMING_CONVENTION.md)
