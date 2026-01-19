# VSCode Extension Assembly Plan

## Overview

Use the Lead Contractor workflow to assemble the generated VSCode extension code into a working extension structure. The 8 feature modules have been generated but need to be integrated into a cohesive, compilable extension.

## Current State

Generated files in `generated/phase3/vscode/`:
- `vscode_scaffolding_code.ts` - Partial (missing JSON configs)
- `vscode_core_code.ts` - extension.ts, types.ts, config.ts, logger.ts
- `vscode_contextprovider_code.ts` - Provider modules + cache.ts
- `vscode_contextmapper_code.ts` - Mapping modules
- `vscode_statusbar_code.ts` - Status bar UI
- `vscode_sidepanel_code.ts` - Tree view UI
- `vscode_decorations_code.ts` - Editor decorations
- `vscode_commands_code.ts` - Commands + final integration

## Target Structure

```
extensions/vscode/
├── package.json
├── tsconfig.json
├── .vscodeignore
├── .eslintrc.json
├── README.md
├── resources/
│   └── icons/
│       ├── red-circle.svg
│       ├── orange-circle.svg
│       └── yellow-circle.svg
└── src/
    ├── extension.ts          # Main entry point
    ├── types.ts              # TypeScript interfaces
    ├── config.ts             # Configuration management
    ├── logger.ts             # Output channel logging
    ├── cache.ts              # Generic TTL cache
    ├── providers/
    │   ├── index.ts
    │   ├── contextProvider.ts
    │   ├── localConfigProvider.ts
    │   ├── cliProvider.ts
    │   └── kubernetesProvider.ts
    ├── mapping/
    │   ├── index.ts
    │   ├── contextMapper.ts
    │   ├── patternMatcher.ts
    │   └── workspaceScanner.ts
    ├── ui/
    │   ├── statusBar.ts
    │   ├── statusBarTooltip.ts
    │   ├── sidePanel/
    │   │   ├── index.ts
    │   │   ├── projectTreeProvider.ts
    │   │   └── contextTreeItem.ts
    │   └── decorations/
    │       ├── index.ts
    │       ├── decorationProvider.ts
    │       ├── sloDecorations.ts
    │       └── riskDecorations.ts
    ├── commands/
    │   ├── index.ts
    │   ├── refreshContext.ts
    │   ├── showImpact.ts
    │   ├── openDashboard.ts
    │   └── showRisks.ts
    └── utils/
        └── cliRunner.ts
```

## Lead Contractor Tasks

### Task 3.3A: Package Configuration

Generate the complete package.json and config files for the extension.

```python
ASSEMBLY_PACKAGE_CONFIG_TASK = """
Create the complete VSCode extension configuration files.

## Goal
Generate production-ready package.json, tsconfig.json, and supporting config files.

## Requirements

1. Create package.json with:
   - name: "contextcore-vscode"
   - displayName: "ContextCore"
   - description: "ProjectContext awareness in your editor"
   - version: "0.1.0"
   - publisher: "contextcore"
   - engines.vscode: "^1.85.0"
   - categories: ["Other", "Visualization"]
   - activationEvents: ["workspaceContains:**/.contextcore", "workspaceContains:**/.contextcore.yaml", "workspaceContains:**/projectcontext.yaml"]
   - main: "./out/extension.js"
   - contributes:
     - configuration:
       - contextcore.kubeconfig (string, default "")
       - contextcore.namespace (string, default "default")
       - contextcore.showInlineHints (boolean, default true)
       - contextcore.refreshInterval (number, default 30, min 5, max 300)
       - contextcore.grafanaUrl (string, default "http://localhost:3000")
     - viewsContainers.activitybar: id "contextcore", title "ContextCore", icon "resources/icons/contextcore.svg"
     - views.contextcore: projectView, risksView, requirementsView
     - commands: contextcore.refresh, contextcore.showImpact, contextcore.openDashboard, contextcore.showRisks, contextcore.statusBarClick
   - scripts: compile, watch, package, lint, test, vscode:prepublish
   - devDependencies: typescript@^5.3.0, @types/vscode@^1.85.0, @types/node@^20.0.0, @vscode/vsce@^2.22.0, eslint@^8.56.0, @typescript-eslint/parser@^6.0.0, @typescript-eslint/eslint-plugin@^6.0.0
   - dependencies: yaml@^2.3.0, @kubernetes/client-node@^0.20.0

2. Create tsconfig.json with strict TypeScript settings

3. Create .vscodeignore excluding dev files

4. Create .eslintrc.json with TypeScript rules

## Output Format
Provide complete JSON content for each file, properly formatted.
"""
```

### Task 3.3B: Core Module Assembly

Assemble the core modules with proper imports and exports.

```python
ASSEMBLY_CORE_MODULES_TASK = """
Assemble the core infrastructure modules for the ContextCore VSCode extension.

## Goal
Create production-ready core modules with proper imports, exports, and integration.

## Input Context
Use the generated code from vscode_core_code.ts as the base, but ensure:
- All imports reference the correct relative paths
- Exports are properly defined for cross-module usage
- Types are consistent across modules

## Requirements

1. Create src/types.ts:
   - Export all interfaces: ProjectContext, ProjectMetadata, ProjectContextSpec, BusinessContext, Requirements, Risk, Target, Design
   - Add ContextCoreConfig interface for extension configuration
   - Ensure types match the CRD schema from crds/projectcontext.yaml

2. Create src/config.ts:
   - Export CONFIG_KEYS constant with all configuration keys
   - Export getConfig<T>(key, defaultValue) function
   - Export onConfigChange(callback) function returning Disposable

3. Create src/logger.ts:
   - Export initialize(), log(message, level), showError(message), dispose()
   - Use output channel named "ContextCore"

4. Create src/cache.ts:
   - Export generic Cache<T> class with TTL support
   - Methods: get(key), set(key, value, ttlMs?), invalidate(key), clear(), size()

## Output Format
Provide complete TypeScript files with proper imports and JSDoc comments.
"""
```

### Task 3.3C: Provider Assembly

Assemble the provider modules.

```python
ASSEMBLY_PROVIDERS_TASK = """
Assemble the context provider modules for the ContextCore VSCode extension.

## Goal
Create the provider layer that loads ProjectContext from multiple sources.

## Input Context
Use generated code from vscode_contextprovider_code.ts, ensuring proper integration.

## Requirements

1. Create src/providers/index.ts:
   - Re-export ContextProvider class
   - Re-export provider functions

2. Create src/providers/contextProvider.ts:
   - Import from ../types, ../cache, ./localConfigProvider, ./cliProvider, ./kubernetesProvider
   - Implement ContextProvider class with:
     - getContext(workspaceFolder): Promise<ProjectContext | undefined>
     - refresh(): Promise<void>
     - onContextChange event
     - dispose() cleanup

3. Create src/providers/localConfigProvider.ts:
   - Export loadLocalConfig(workspaceFolder): Promise<ProjectContext | undefined>
   - Support .contextcore, .contextcore.yaml files
   - Use 'yaml' package for parsing

4. Create src/providers/cliProvider.ts:
   - Export loadFromCli(workspaceFolder): Promise<ProjectContext | undefined>
   - Execute: contextcore context show --format json
   - Handle command not found gracefully

5. Create src/providers/kubernetesProvider.ts:
   - Export loadFromKubernetes(name, namespace): Promise<ProjectContext | undefined>
   - Use @kubernetes/client-node
   - Return undefined if kubeconfig not available (don't throw)

## Output Format
Provide complete TypeScript files ready to drop into src/providers/.
"""
```

### Task 3.3D: Mapping Assembly

Assemble the file-to-context mapping modules.

```python
ASSEMBLY_MAPPING_TASK = """
Assemble the context mapping modules for the ContextCore VSCode extension.

## Goal
Create the mapping layer that associates files with their ProjectContext.

## Input Context
Use generated code from vscode_contextmapper_code.ts.

## Requirements

1. Create src/mapping/index.ts:
   - Re-export ContextMapper class
   - Re-export helper functions

2. Create src/mapping/contextMapper.ts:
   - Import from ../providers, ./patternMatcher, ./workspaceScanner
   - Implement ContextMapper class with:
     - constructor(contextProvider: ContextProvider)
     - initialize(): Promise<void>
     - getContextForFile(uri): ProjectContext | undefined
     - getContextForDocument(document): ProjectContext | undefined
     - dispose()
   - Use LRU cache for performance

3. Create src/mapping/patternMatcher.ts:
   - Export matchesPattern(filePath, pattern): boolean
   - Support glob patterns: *, **, ?
   - Support negation with ! prefix

4. Create src/mapping/workspaceScanner.ts:
   - Export findContextFiles(folder): Promise<Uri[]>
   - Look for .contextcore, .contextcore.yaml, projectcontext.yaml
   - Exclude node_modules

## Output Format
Provide complete TypeScript files ready to drop into src/mapping/.
"""
```

### Task 3.3E: UI Assembly

Assemble the UI components.

```python
ASSEMBLY_UI_TASK = """
Assemble the UI components for the ContextCore VSCode extension.

## Goal
Create status bar, side panel tree view, and editor decorations.

## Input Context
Use generated code from vscode_statusbar_code.ts, vscode_sidepanel_code.ts, vscode_decorations_code.ts.

## Requirements

1. Create src/ui/statusBar.ts:
   - Import from ../mapping
   - Implement ContextStatusBar class
   - Show criticality icon and project ID
   - Handle click to show quick pick menu

2. Create src/ui/statusBarTooltip.ts:
   - Export buildTooltip(context): MarkdownString

3. Create src/ui/sidePanel/index.ts:
   - Re-export ProjectTreeProvider, ContextTreeItem, TreeItemType

4. Create src/ui/sidePanel/contextTreeItem.ts:
   - Export TreeItemType enum
   - Export ContextTreeItem class extending TreeItem

5. Create src/ui/sidePanel/projectTreeProvider.ts:
   - Implement TreeDataProvider<ContextTreeItem>
   - Show project hierarchy: Business, Risks, Requirements, Targets

6. Create src/ui/decorations/index.ts:
   - Re-export DecorationProvider

7. Create src/ui/decorations/decorationProvider.ts:
   - Implement DecorationProvider class
   - Respect contextcore.showInlineHints config

8. Create src/ui/decorations/sloDecorations.ts:
   - Export findHttpHandlers, findDatabaseQueries, findExternalCalls
   - Export buildSloDecoration

9. Create src/ui/decorations/riskDecorations.ts:
   - Export isFileInRiskScope, buildRiskDecoration

## Output Format
Provide complete TypeScript files ready to drop into src/ui/.
"""
```

### Task 3.3F: Commands and Extension Entry Point

Assemble commands and the main extension entry point.

```python
ASSEMBLY_COMMANDS_TASK = """
Assemble the commands and main extension entry point.

## Goal
Create all commands and wire everything together in extension.ts.

## Input Context
Use generated code from vscode_commands_code.ts.

## Requirements

1. Create src/commands/index.ts:
   - Re-export all command creators

2. Create src/commands/refreshContext.ts:
   - Export createRefreshCommand(contextProvider): Disposable
   - Command: contextcore.refresh

3. Create src/commands/showImpact.ts:
   - Export createShowImpactCommand(contextMapper): Disposable
   - Command: contextcore.showImpact
   - Run CLI: contextcore graph impact --project <id>

4. Create src/commands/openDashboard.ts:
   - Export createOpenDashboardCommand(contextMapper): Disposable
   - Command: contextcore.openDashboard
   - Open Grafana URL with project filter

5. Create src/commands/showRisks.ts:
   - Export createShowRisksCommand(contextMapper): Disposable
   - Command: contextcore.showRisks
   - Show quick pick grouped by priority

6. Create src/utils/cliRunner.ts:
   - Export runContextCoreCommand(command): Promise<string>

7. Create src/extension.ts (CRITICAL - main entry point):
   - Import all modules
   - activate(context: ExtensionContext):
     a. Initialize logger
     b. Create ContextProvider
     c. Create ContextMapper and initialize
     d. Create ContextStatusBar
     e. Register ProjectTreeProvider for views
     f. Create DecorationProvider
     g. Register all commands
     h. Add all disposables to context.subscriptions
     i. Log activation complete
   - deactivate(): cleanup

## Output Format
Provide complete TypeScript files. extension.ts must be fully integrated.
"""
```

### Task 3.3G: Resources and Final Verification

Create resource files and verify the extension structure.

```python
ASSEMBLY_RESOURCES_TASK = """
Create resource files and generate a verification checklist.

## Goal
Create SVG icons and verify the complete extension structure.

## Requirements

1. Create resources/icons/contextcore.svg:
   - Simple icon for activity bar (24x24)
   - Use a context/graph theme

2. Create resources/icons/red-circle.svg:
   - Red filled circle for P1 risks (16x16)

3. Create resources/icons/orange-circle.svg:
   - Orange filled circle for P2 risks (16x16)

4. Create resources/icons/yellow-circle.svg:
   - Yellow filled circle for P3 risks (16x16)

5. Create README.md for the extension:
   - Features overview with screenshots placeholders
   - Installation instructions
   - Configuration reference
   - Usage guide

6. Provide verification checklist:
   - All files exist in correct locations
   - All imports are valid
   - package.json commands match registered commands
   - package.json views match registered tree providers

## Output Format
Provide SVG content and README markdown. Include verification checklist.
"""
```

## Implementation Order

1. **Task 3.3A**: Package Configuration (creates build foundation)
2. **Task 3.3B**: Core Module Assembly (types, config, logger, cache)
3. **Task 3.3C**: Provider Assembly (data loading layer)
4. **Task 3.3D**: Mapping Assembly (file-to-context layer)
5. **Task 3.3E**: UI Assembly (visual components)
6. **Task 3.3F**: Commands and Extension Entry Point (integration)
7. **Task 3.3G**: Resources and Final Verification

## Adding to Lead Contractor

Add these tasks to `scripts/lead_contractor/tasks/vscode_assembly.py`:

```python
ASSEMBLY_FEATURES = [
    Feature(
        task=ASSEMBLY_PACKAGE_CONFIG_TASK,
        name="Assembly_PackageConfig",
        is_typescript=True,
        output_subdir="vscode_assembly",
    ),
    Feature(
        task=ASSEMBLY_CORE_MODULES_TASK,
        name="Assembly_CoreModules",
        is_typescript=True,
        output_subdir="vscode_assembly",
    ),
    Feature(
        task=ASSEMBLY_PROVIDERS_TASK,
        name="Assembly_Providers",
        is_typescript=True,
        output_subdir="vscode_assembly",
    ),
    Feature(
        task=ASSEMBLY_MAPPING_TASK,
        name="Assembly_Mapping",
        is_typescript=True,
        output_subdir="vscode_assembly",
    ),
    Feature(
        task=ASSEMBLY_UI_TASK,
        name="Assembly_UI",
        is_typescript=True,
        output_subdir="vscode_assembly",
    ),
    Feature(
        task=ASSEMBLY_COMMANDS_TASK,
        name="Assembly_Commands",
        is_typescript=True,
        output_subdir="vscode_assembly",
    ),
    Feature(
        task=ASSEMBLY_RESOURCES_TASK,
        name="Assembly_Resources",
        is_typescript=True,
        output_subdir="vscode_assembly",
    ),
]
```

## Running the Assembly

```bash
# Run all assembly tasks
PYTHONPATH="/Users/neilyashinsky/Documents/dev/startd8-sdk/src:$PYTHONPATH" \
python3 scripts/lead_contractor/run_vscode_assembly.py

# Or run individual tasks
PYTHONPATH="/Users/neilyashinsky/Documents/dev/startd8-sdk/src:$PYTHONPATH" \
python3 scripts/lead_contractor/run_vscode_assembly.py --feature 1
```

## Post-Assembly Steps

After lead contractor generates the assembly code:

1. Create directory structure:
   ```bash
   mkdir -p extensions/vscode/src/{providers,mapping,ui/{sidePanel,decorations},commands,utils}
   mkdir -p extensions/vscode/resources/icons
   ```

2. Copy generated files to correct locations

3. Install dependencies and verify:
   ```bash
   cd extensions/vscode
   npm install
   npm run compile
   ```

4. Test in Extension Development Host (F5 in VSCode)

## Success Criteria

- [ ] `npm install` completes without errors
- [ ] `npm run compile` produces no TypeScript errors
- [ ] Extension activates when .contextcore file present
- [ ] Status bar shows project criticality
- [ ] Side panel displays project tree
- [ ] Commands work: refresh, showImpact, openDashboard, showRisks
- [ ] Inline decorations appear on HTTP handlers (when enabled)
