# VSCode Extension Plan: ContextCore IDE Integration

## Overview

Add a VSCode extension as an optional module within the ContextCore repository. The extension surfaces ProjectContext information directly in the development environment, providing real-time awareness of requirements, risks, and constraints.

## Architecture Decision

### Repository Structure

Use an `extensions/` directory to clearly separate optional TypeScript code from core Python:

```
ContextCore/
├── src/contextcore/           # Core Python SDK
├── extensions/
│   └── vscode/                # VSCode extension (TypeScript)
│       ├── package.json
│       ├── tsconfig.json
│       ├── src/
│       ├── resources/
│       └── README.md
├── scripts/
│   └── run_lead_contractor_phase3.py  # Updated with extension tasks
└── pyproject.toml             # Python project (unchanged)
```

### Why This Structure

1. **Clear separation**: TypeScript code isolated from Python
2. **Optional**: Can be ignored by Python-only users
3. **Independent versioning**: Extension can have its own release cycle
4. **Standard pattern**: Follows monorepo conventions (like Grafana, VSCode itself)

## Communication Architecture

The extension communicates with ContextCore via multiple channels:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     VSCode Extension                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐    │
│  │ Local Config │   │  CLI Bridge  │   │  K8s Client          │    │
│  │              │   │              │   │  (optional)          │    │
│  │ .contextcore │   │ contextcore  │   │                      │    │
│  │ file in      │   │ CLI commands │   │ Direct CRD access    │    │
│  │ workspace    │   │ via shell    │   │ when kubeconfig      │    │
│  └──────┬───────┘   └──────┬───────┘   │ available            │    │
│         │                  │           └──────────┬───────────┘    │
│         │                  │                      │                 │
│         └────────┬─────────┴──────────────────────┘                 │
│                  │                                                   │
│                  ▼                                                   │
│         ┌────────────────┐                                          │
│         │ Context Cache  │  In-memory cache with TTL                │
│         │                │  Refreshed on file save / interval       │
│         └────────────────┘                                          │
│                  │                                                   │
│                  ▼                                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    UI Components                               │  │
│  │  • Status Bar (criticality badge)                             │  │
│  │  • Activity Bar + Side Panel (full context view)              │  │
│  │  • Editor Decorations (inline SLO hints)                      │  │
│  │  • Hover Provider (requirement details)                       │  │
│  │  • CodeLens (risk indicators)                                 │  │
│  │  • Diagnostics (constraint violations)                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow Priority

1. **Local `.contextcore` file** (fastest, always available)
2. **CLI commands** (reliable, works offline)
3. **Direct K8s API** (live updates, requires cluster access)

## Module Breakdown

### Module 1: Project Scaffolding

Create the extension project structure with all configuration files.

**Files to create:**
- `extensions/vscode/package.json` - Extension manifest
- `extensions/vscode/tsconfig.json` - TypeScript config
- `extensions/vscode/.vscodeignore` - Package exclusions
- `extensions/vscode/.eslintrc.json` - Linting rules
- `extensions/vscode/README.md` - Extension documentation

### Module 2: Core Infrastructure

Base classes and utilities for the extension.

**Files to create:**
- `src/extension.ts` - Entry point (activate/deactivate)
- `src/types.ts` - TypeScript interfaces matching Python models
- `src/config.ts` - Extension configuration management
- `src/logger.ts` - Output channel logging

### Module 3: Context Provider

Load and cache ProjectContext data from various sources.

**Files to create:**
- `src/providers/contextProvider.ts` - Main context loading logic
- `src/providers/localConfigProvider.ts` - Read `.contextcore` files
- `src/providers/cliProvider.ts` - Shell out to `contextcore` CLI
- `src/providers/kubernetesProvider.ts` - Direct K8s API (optional)
- `src/cache.ts` - In-memory cache with TTL

### Module 4: File-to-Context Mapping

Map workspace files to their relevant ProjectContext.

**Files to create:**
- `src/mapping/contextMapper.ts` - Core mapping logic
- `src/mapping/patternMatcher.ts` - Glob pattern matching for risk scopes
- `src/mapping/workspaceScanner.ts` - Scan workspace for context files

### Module 5: Status Bar

Show project criticality in the status bar.

**Files to create:**
- `src/ui/statusBar.ts` - Status bar item with criticality badge
- `src/ui/statusBarTooltip.ts` - Rich tooltip content

### Module 6: Side Panel (Tree View)

Activity bar icon and side panel with full context view.

**Files to create:**
- `src/ui/sidePanel/projectTreeProvider.ts` - Tree data provider
- `src/ui/sidePanel/contextTreeItem.ts` - Tree item rendering
- `src/ui/sidePanel/riskTreeItem.ts` - Risk display
- `src/ui/sidePanel/requirementTreeItem.ts` - SLO display

### Module 7: Editor Decorations

Inline hints showing SLO requirements near relevant code.

**Files to create:**
- `src/ui/decorations/decorationProvider.ts` - Main decoration logic
- `src/ui/decorations/sloDecorations.ts` - Latency/throughput hints
- `src/ui/decorations/riskDecorations.ts` - Gutter icons for risk scope

### Module 8: Hover Provider

Rich hover cards with requirement details.

**Files to create:**
- `src/ui/hover/hoverProvider.ts` - Hover information provider
- `src/ui/hover/requirementHover.ts` - SLO details on hover
- `src/ui/hover/riskHover.ts` - Risk details on hover

### Module 9: CodeLens

Inline actions and indicators above functions.

**Files to create:**
- `src/ui/codelens/codeLensProvider.ts` - CodeLens provider
- `src/ui/codelens/sloCodeLens.ts` - "SLO: P99 < 200ms" above handlers

### Module 10: Diagnostics

Problem matcher for constraint violations.

**Files to create:**
- `src/diagnostics/diagnosticProvider.ts` - Diagnostic collection
- `src/diagnostics/constraintChecker.ts` - Check code against constraints

### Module 11: Commands

Extension commands for user interaction.

**Files to create:**
- `src/commands/refreshContext.ts` - Refresh context data
- `src/commands/showImpact.ts` - Show impact analysis
- `src/commands/openDashboard.ts` - Open Grafana dashboard
- `src/commands/showRisks.ts` - Show all risks for current file

## Lead Contractor Task Specifications

### Task 3.2A: Extension Scaffolding

```python
FEATURE_3_2A_TASK = """
Create the VSCode extension project scaffolding for ContextCore.

## Goal
Set up a complete VSCode extension project structure with all necessary
configuration files, ready for TypeScript development.

## Context
- Extension will be at extensions/vscode/ within the ContextCore repo
- Extension name: contextcore-vscode
- Display name: ContextCore
- Publisher: contextcore (placeholder)
- Minimum VSCode version: 1.85.0

## Requirements

1. Create package.json with:
   - name: "contextcore-vscode"
   - displayName: "ContextCore"
   - description: "ProjectContext awareness in your editor"
   - version: "0.1.0"
   - engines.vscode: "^1.85.0"
   - categories: ["Other", "Visualization"]
   - activationEvents: ["workspaceContains:**/.contextcore", "workspaceContains:**/projectcontext.yaml"]
   - main: "./out/extension.js"
   - contributes:
     - configuration (contextcore.kubeconfig, contextcore.namespace, contextcore.showInlineHints)
     - viewsContainers.activitybar (contextcore icon)
     - views.contextcore (projectView, risksView, requirementsView)
     - commands (refresh, showImpact, openDashboard)
   - scripts: compile, watch, package, lint, test
   - devDependencies: typescript, @types/vscode, @types/node, eslint, vsce

2. Create tsconfig.json with:
   - target: ES2020
   - module: commonjs
   - lib: ["ES2020"]
   - outDir: "./out"
   - rootDir: "./src"
   - strict: true
   - esModuleInterop: true
   - skipLibCheck: true

3. Create .vscodeignore with standard exclusions

4. Create .eslintrc.json with TypeScript rules

5. Create README.md with:
   - Features overview
   - Installation instructions
   - Configuration options
   - Screenshots placeholders

## Output Format
Provide the complete content of each file. Use JSON for config files.
"""
```

### Task 3.2B: Core Infrastructure

```python
FEATURE_3_2B_TASK = """
Implement the core infrastructure for the ContextCore VSCode extension.

## Goal
Create the extension entry point and foundational utilities that all
other modules depend on.

## Context
- TypeScript extension for VSCode
- Located at extensions/vscode/src/
- Must handle activation and deactivation cleanly

## Requirements

1. Create src/extension.ts:
   - export function activate(context: vscode.ExtensionContext)
   - export function deactivate()
   - Initialize all providers in activate()
   - Register all disposables with context.subscriptions
   - Log activation to output channel

2. Create src/types.ts with interfaces:
   - ProjectContext (matching Python ProjectContextSpec)
   - ProjectMetadata (id, namespace, name)
   - BusinessContext (criticality, value, owner, costCenter)
   - Requirements (availability, latencyP99, latencyP50, throughput, errorBudget)
   - Risk (type, priority, description, scope, mitigation)
   - Target (kind, name, namespace)
   - Design (adr, doc, apiContract)

3. Create src/config.ts:
   - getConfig<T>(key: string): T
   - onConfigChange(callback): Disposable
   - Configuration keys: kubeconfig, namespace, showInlineHints, refreshInterval

4. Create src/logger.ts:
   - Create output channel "ContextCore"
   - log(message: string, level?: 'info' | 'warn' | 'error')
   - Show output channel on error

## Output Format
Provide clean TypeScript code with proper types and JSDoc comments.
"""
```

### Task 3.2C: Context Provider

```python
FEATURE_3_2C_TASK = """
Implement the context provider system for loading ProjectContext data.

## Goal
Create a provider system that loads ProjectContext from multiple sources
with caching and automatic refresh.

## Context
- TypeScript for VSCode extension
- Must support: local .contextcore files, CLI commands, K8s API
- Should gracefully degrade if sources unavailable

## Requirements

1. Create src/providers/contextProvider.ts:
   - class ContextProvider
   - async getContext(workspaceFolder: string): Promise<ProjectContext | undefined>
   - async refresh(): Promise<void>
   - onContextChange: Event<ProjectContext>
   - Try sources in order: local -> CLI -> K8s

2. Create src/providers/localConfigProvider.ts:
   - Read .contextcore YAML file from workspace root
   - Parse and validate against ProjectContext interface
   - Watch for file changes

3. Create src/providers/cliProvider.ts:
   - Execute: contextcore context show --format json
   - Parse JSON output into ProjectContext
   - Handle command not found gracefully

4. Create src/providers/kubernetesProvider.ts:
   - Use @kubernetes/client-node package
   - Load kubeconfig from config or default location
   - Fetch ProjectContext CRD by name/namespace
   - Optional - skip if kubeconfig not available

5. Create src/cache.ts:
   - class ContextCache
   - get(key: string): T | undefined
   - set(key: string, value: T, ttlMs: number): void
   - invalidate(key: string): void
   - Default TTL: 30 seconds

## Output Format
Provide clean TypeScript with async/await, proper error handling, and types.
"""
```

### Task 3.2D: Context Mapper

```python
FEATURE_3_2D_TASK = """
Implement file-to-context mapping for the VSCode extension.

## Goal
Map workspace files to their relevant ProjectContext based on configuration,
risk scopes, and target patterns.

## Context
- A workspace may have multiple ProjectContexts
- Files can match via: .contextcore config, risk.scope patterns, target names
- Should efficiently handle large workspaces

## Requirements

1. Create src/mapping/contextMapper.ts:
   - class ContextMapper
   - async initialize(workspaceFolders: readonly WorkspaceFolder[]): Promise<void>
   - getContextForFile(uri: Uri): ProjectContext | undefined
   - getContextForDocument(document: TextDocument): ProjectContext | undefined
   - Support multi-root workspaces

2. Create src/mapping/patternMatcher.ts:
   - matchesPattern(filePath: string, pattern: string): boolean
   - Support glob patterns: *, **, ?
   - Support negation: !pattern
   - Cache compiled patterns for performance

3. Create src/mapping/workspaceScanner.ts:
   - async scanWorkspace(folder: WorkspaceFolder): Promise<ContextMapping[]>
   - Find all .contextcore files
   - Build file -> context mapping
   - Watch for new .contextcore files

4. Mapping priority:
   - Exact .contextcore file in directory
   - risk.scope pattern match
   - Closest parent directory with .contextcore
   - Default workspace context

## Output Format
Provide TypeScript with efficient algorithms and proper VSCode API usage.
"""
```

### Task 3.2E: Status Bar

```python
FEATURE_3_2E_TASK = """
Implement the status bar component showing project criticality.

## Goal
Display current file's project context and criticality in the VSCode
status bar, with quick access to more details.

## Context
- Status bar items appear at bottom of VSCode window
- Should update when active editor changes
- Click should show quick pick or open side panel

## Requirements

1. Create src/ui/statusBar.ts:
   - class ContextStatusBar implements Disposable
   - constructor(contextMapper: ContextMapper)
   - update(editor: TextEditor | undefined): void
   - dispose(): void

2. Status bar display:
   - Icon based on criticality: $(flame) critical, $(warning) high, $(info) medium, $(check) low
   - Text: project ID
   - Background color: error for critical, warning for high
   - Tooltip: rich markdown with project details

3. Create src/ui/statusBarTooltip.ts:
   - buildTooltip(context: ProjectContext): MarkdownString
   - Include: project ID, criticality, owner, risk count, SLO summary
   - Link to "Click for details"

4. Click action:
   - Show quick pick with options:
     - "Show Full Context" -> reveal side panel
     - "Show Impact Analysis" -> run impact command
     - "Open in Grafana" -> open dashboard URL

## Output Format
Provide TypeScript using vscode.window.createStatusBarItem API.
"""
```

### Task 3.2F: Side Panel

```python
FEATURE_3_2F_TASK = """
Implement the side panel tree view for full context display.

## Goal
Create an activity bar view that shows the complete ProjectContext
as an expandable tree with projects, risks, and requirements.

## Context
- Activity bar icon appears in left sidebar
- Tree view shows hierarchical data
- Should refresh when context changes

## Requirements

1. Create src/ui/sidePanel/projectTreeProvider.ts:
   - class ProjectTreeProvider implements TreeDataProvider<ContextTreeItem>
   - getTreeItem(element): TreeItem
   - getChildren(element?): ContextTreeItem[]
   - refresh(): void
   - onDidChangeTreeData: Event

2. Create src/ui/sidePanel/contextTreeItem.ts:
   - class ContextTreeItem extends TreeItem
   - Support types: project, section, risk, requirement, target
   - Icons for each type
   - Collapsible state based on children

3. Tree structure:
   ```
   📦 checkout-service
   ├── 📋 Business
   │   ├── Criticality: critical
   │   ├── Owner: commerce-team
   │   └── Value: $2M/day
   ├── ⚠️ Risks (3)
   │   ├── 🔴 P1: PCI compliance
   │   ├── 🟠 P2: Rate limiting
   │   └── 🟡 P3: Documentation
   ├── 📊 Requirements
   │   ├── Availability: 99.95%
   │   ├── Latency P99: 200ms
   │   └── Throughput: 1000 rps
   └── 🎯 Targets (2)
       ├── Deployment: checkout
       └── Service: checkout-svc
   ```

4. Context menu actions:
   - Copy value
   - Show in Grafana
   - View impact (for projects)

## Output Format
Provide TypeScript using vscode.window.registerTreeDataProvider API.
"""
```

### Task 3.2G: Editor Decorations

```python
FEATURE_3_2G_TASK = """
Implement editor decorations for inline SLO hints.

## Goal
Show SLO requirements as inline hints near relevant code patterns
(HTTP handlers, database queries, external calls).

## Context
- Decorations appear after line content
- Should be subtle but informative
- Can be toggled via configuration

## Requirements

1. Create src/ui/decorations/decorationProvider.ts:
   - class DecorationProvider implements Disposable
   - updateDecorations(editor: TextEditor): void
   - Register for onDidChangeActiveTextEditor
   - Register for onDidChangeTextEditorSelection
   - Respect contextcore.showInlineHints config

2. Create src/ui/decorations/sloDecorations.ts:
   - findHttpHandlers(document: TextDocument): Range[]
   - findDatabaseCalls(document: TextDocument): Range[]
   - findExternalCalls(document: TextDocument): Range[]
   - Pattern matching for Python, TypeScript, Go

3. Decoration types:
   - Latency hint: "// SLO: P99 < 200ms" (gray, italic, after line)
   - Throughput hint: "// SLO: 1000 rps"
   - Availability hint: "// SLO: 99.95%"

4. Create src/ui/decorations/riskDecorations.ts:
   - Gutter icon for files in risk.scope
   - Red dot for P1, orange for P2, yellow for P3
   - Hover shows risk description

5. Code patterns to detect:
   - Python: def get_, def post_, @app.route, async def handle
   - TypeScript: app.get(, app.post(, async function handle
   - Go: func (h *Handler), http.HandleFunc

## Output Format
Provide TypeScript using vscode.window.createTextEditorDecorationType API.
"""
```

### Task 3.2H: Commands and Integration

```python
FEATURE_3_2H_TASK = """
Implement extension commands and final integration.

## Goal
Create user-facing commands and wire everything together in the
main extension activation.

## Context
- Commands appear in command palette (Ctrl+Shift+P)
- Should integrate with existing contextcore CLI
- Provide quick access to common actions

## Requirements

1. Create src/commands/refreshContext.ts:
   - Command: contextcore.refresh
   - Invalidate cache and reload all contexts
   - Show notification on completion

2. Create src/commands/showImpact.ts:
   - Command: contextcore.showImpact
   - Run: contextcore graph impact --project <current>
   - Display results in webview or output channel
   - Show affected projects and blast radius

3. Create src/commands/openDashboard.ts:
   - Command: contextcore.openDashboard
   - Build Grafana URL with project filter
   - Open in external browser
   - URL pattern: {grafanaUrl}/d/contextcore-project?var-project={projectId}

4. Create src/commands/showRisks.ts:
   - Command: contextcore.showRisks
   - Show quick pick with all risks for current context
   - Group by priority (P1, P2, P3, P4)
   - Select to jump to risk scope in editor

5. Update src/extension.ts activate():
   - Initialize ContextProvider
   - Initialize ContextMapper
   - Create StatusBar
   - Register TreeDataProvider
   - Register DecorationProvider
   - Register all commands
   - Register configuration change listener

## Output Format
Provide TypeScript with proper command registration and error handling.
"""
```

## Implementation Order

1. **Phase A**: Scaffolding (Task 3.2A) - Project setup
2. **Phase B**: Core (Task 3.2B) - Entry point and types
3. **Phase C**: Data Layer (Tasks 3.2C, 3.2D) - Context loading and mapping
4. **Phase D**: UI Components (Tasks 3.2E, 3.2F, 3.2G) - Visual features
5. **Phase E**: Integration (Task 3.2H) - Commands and final wiring

## Build and Package

```bash
# Development
cd extensions/vscode
npm install
npm run compile
# Press F5 in VSCode to launch Extension Development Host

# Package
npm run package  # Creates contextcore-vscode-0.1.0.vsix

# Install locally
code --install-extension contextcore-vscode-0.1.0.vsix
```

## Integration with Python CLI

Add a new CLI command to support the extension:

```bash
# New command for extension to call
contextcore context show --format json --project <id>

# Returns ProjectContext as JSON for extension to parse
```

## Testing Strategy

1. **Unit tests**: Jest for TypeScript logic
2. **Integration tests**: VSCode extension test framework
3. **Manual testing**: Extension Development Host

## Success Criteria

- [ ] Extension activates when .contextcore file present
- [ ] Status bar shows project criticality for current file
- [ ] Side panel displays full ProjectContext tree
- [ ] Inline decorations show SLO hints near HTTP handlers
- [ ] Gutter icons indicate files in risk scope
- [ ] Commands work: refresh, showImpact, openDashboard
- [ ] Works offline with local .contextcore files
- [ ] Gracefully handles missing kubeconfig
