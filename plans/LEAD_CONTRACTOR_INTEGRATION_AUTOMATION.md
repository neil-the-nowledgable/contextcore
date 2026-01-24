# Lead Contractor Integration Automation Plan

**Problem**: The Lead Contractor workflow generates code but doesn't automatically integrate it into the source tree. There's a backlog of 61+ generated code files waiting for manual integration.

**Goal**: Automate code integration while maintaining safety and reviewability.

---

## Current State Analysis

### Generated Code Inventory
- **61+ code files** across multiple directories:
  - `generated/phase3/` - Graph, Learning, A2A features
  - `generated/tui/` - TUI implementation
  - `generated/install_tracking/` - Installation tracking features
  - `generated/feature_2_*` - Phase 2 features (SLO tests, PR review)

### Current Workflow
1. Lead Contractor generates code → saves to `generated/`
2. Manual steps required:
   - Review generated code
   - Copy files to correct locations
   - Update imports/exports
   - Test integration
   - Commit changes

---

## Proposed Approaches

### Approach 1: Automatic Integration with File Path Mapping (Recommended)

**Strategy**: Enhance the workflow to automatically place files based on file markers or feature metadata.

#### Implementation

1. **Enhance Feature Model** - Add target path mapping:
```python
@dataclass
class Feature:
    task: str
    name: str
    is_typescript: bool = False
    output_subdir: Optional[str] = None
    # NEW: Target paths for integration
    target_paths: Optional[Dict[str, str]] = None  # {generated_file: target_path}
    integration_mode: str = "manual"  # "auto", "review", "manual"
```

2. **Add Integration Function** to `runner.py`:
```python
def integrate_code(
    result: WorkflowResult,
    feature: Feature,
    dry_run: bool = False,
    require_review: bool = True
) -> IntegrationResult:
    """Integrate generated code into source tree."""
    # Extract files with paths from implementation
    # Map to target locations
    # Copy files (with backup)
    # Update imports if needed
    # Return integration report
```

3. **Integration Modes**:
   - `auto`: Direct integration (use with caution)
   - `review`: Generate diff, wait for approval
   - `manual`: Current behavior (save to generated/)

#### Pros
- ✅ Automatic integration reduces manual work
- ✅ Can be made safe with review mode
- ✅ Handles backlog retroactively

#### Cons
- ⚠️ Requires careful path mapping
- ⚠️ May need import resolution logic

---

### Approach 2: Post-Generation Integration Script

**Strategy**: Create a separate script that processes generated code and integrates it.

#### Implementation

Create `scripts/lead_contractor/integrate.py`:

```python
"""
Integration script for Lead Contractor generated code.

Usage:
    # Review and integrate all pending code
    python3 scripts/lead_contractor/integrate.py --review
    
    # Auto-integrate specific feature
    python3 scripts/lead_contractor/integrate.py --feature graph_schema --auto
    
    # Process backlog
    python3 scripts/lead_contractor/integrate.py --backlog --dry-run
"""

def integrate_backlog(dry_run: bool = False):
    """Process all generated code in backlog."""
    # Scan generated/ directories
    # Match files to target locations
    # Generate integration plan
    # Execute or show preview
```

#### Features
- Scan `generated/` for unintegrated code
- Match files to target locations via heuristics/metadata
- Generate integration plan with diffs
- Support dry-run mode
- Track integration status

#### Pros
- ✅ Separates generation from integration
- ✅ Can process backlog retroactively
- ✅ Safe with dry-run mode

#### Cons
- ⚠️ Requires manual mapping or heuristics
- ⚠️ Additional step in workflow

---

### Approach 3: Feature Metadata-Driven Integration

**Strategy**: Enhance task definitions to include integration metadata.

#### Implementation

Update task definitions to include integration instructions:

```python
FEATURE_3_1A_GRAPH_SCHEMA = Feature(
    task=GRAPH_SCHEMA_TASK,
    name="Feature_3_1A_Graph_Schema",
    target_paths={
        "graph_schema_code.py": "src/contextcore/graph/schema.py"
    },
    integration_steps=[
        "Create src/contextcore/graph/__init__.py",
        "Add exports to __init__.py",
        "Update imports in dependent modules"
    ],
    integration_mode="review"  # auto, review, manual
)
```

#### Pros
- ✅ Explicit integration instructions
- ✅ Self-documenting
- ✅ Can be validated

#### Cons
- ⚠️ Requires updating all existing features
- ⚠️ More verbose task definitions

---

### Approach 4: Hybrid Approach (Recommended for Backlog)

**Strategy**: Combine approaches 1 and 2 - enhance workflow for new code, create backlog processor.

#### Implementation Plan

**Phase 1: Backlog Processing** (Immediate)
1. Create `scripts/lead_contractor/integrate_backlog.py`
2. Scan all generated code
3. Generate integration report
4. Manual review and batch integration

**Phase 2: Enhanced Workflow** (Future)
1. Add integration hooks to `runner.py`
2. Support file path extraction from code blocks
3. Add integration mode to Feature model
4. Generate integration plan automatically

**Phase 3: Integration Tracking**
1. Track which generated files have been integrated
2. Store integration metadata in result JSON
3. Prevent duplicate integrations

---

## Recommended Implementation: Backlog Integration Script

### Script: `scripts/lead_contractor/integrate_backlog.py`

```python
#!/usr/bin/env python3
"""
Process backlog of generated Lead Contractor code.

Scans generated/ directories, identifies unintegrated code,
and provides integration assistance.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class GeneratedFile:
    """Represents a generated code file."""
    path: Path
    feature_name: str
    result_file: Path
    target_path: Optional[Path] = None
    integrated: bool = False

def scan_backlog() -> List[GeneratedFile]:
    """Scan generated/ directories for unintegrated code."""
    generated_files = []
    generated_dir = Path(__file__).parent.parent.parent / "generated"
    
    # Find all *_code.py and *_code.ts files
    for code_file in generated_dir.rglob("*_code.*"):
        # Find corresponding result file
        result_file = code_file.parent / code_file.name.replace("_code.", "_result.")
        
        if result_file.exists():
            with open(result_file) as f:
                result = json.load(f)
                feature_name = result.get("feature", "unknown")
                
                generated_files.append(GeneratedFile(
                    path=code_file,
                    feature_name=feature_name,
                    result_file=result_file,
                    integrated=False  # TODO: Check integration status
                ))
    
    return generated_files

def infer_target_path(generated_file: GeneratedFile) -> Optional[Path]:
    """Infer target path from feature name and file content."""
    # Heuristics:
    # - graph_* -> src/contextcore/graph/
    # - a2a_* -> src/contextcore/agent/
    # - tui_* -> src/contextcore/tui/
    # - install_* -> scripts/
    
    feature = generated_file.feature_name.lower()
    project_root = Path(__file__).parent.parent.parent
    
    if "graph" in feature:
        return project_root / "src" / "contextcore" / "graph" / generated_file.path.name.replace("_code", "")
    elif "a2a" in feature or "adapter" in feature:
        return project_root / "src" / "contextcore" / "agent" / generated_file.path.name.replace("_code", "")
    elif "tui" in feature:
        return project_root / "src" / "contextcore" / "tui" / generated_file.path.name.replace("_code", "")
    elif "install" in feature:
        return project_root / "scripts" / generated_file.path.name.replace("_code", "")
    
    return None

def generate_integration_plan(files: List[GeneratedFile]) -> Dict:
    """Generate integration plan with target paths."""
    plan = {
        "files": [],
        "warnings": [],
        "requires_review": []
    }
    
    for file in files:
        target = infer_target_path(file)
        if target:
            plan["files"].append({
                "source": str(file.path),
                "target": str(target),
                "feature": file.feature_name
            })
        else:
            plan["warnings"].append(f"Could not infer target for {file.path}")
            plan["requires_review"].append(file)
    
    return plan

def integrate_file(source: Path, target: Path, dry_run: bool = False) -> bool:
    """Integrate a single file."""
    if dry_run:
        print(f"[DRY RUN] Would copy {source} -> {target}")
        return True
    
    # Create backup if target exists
    if target.exists():
        backup = target.with_suffix(f"{target.suffix}.backup")
        shutil.copy2(target, backup)
        print(f"Backed up existing file to {backup}")
    
    # Create target directory
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    shutil.copy2(source, target)
    print(f"Integrated: {target}")
    
    return True

def main():
    """Main integration workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrate Lead Contractor generated code")
    parser.add_argument("--dry-run", action="store_true", help="Preview without integrating")
    parser.add_argument("--feature", help="Process specific feature")
    parser.add_argument("--list", action="store_true", help="List all pending integrations")
    parser.add_argument("--auto", action="store_true", help="Auto-integrate without review")
    
    args = parser.parse_args()
    
    # Scan backlog
    files = scan_backlog()
    
    if args.list:
        print(f"\nFound {len(files)} generated files:")
        for f in files:
            target = infer_target_path(f)
            status = "✓" if target else "?"
            print(f"  {status} {f.feature_name}: {f.path.name}")
            if target:
                print(f"    -> {target}")
        return
    
    # Generate integration plan
    plan = generate_integration_plan(files)
    
    print(f"\nIntegration Plan:")
    print(f"  Files to integrate: {len(plan['files'])}")
    print(f"  Requires review: {len(plan['requires_review'])}")
    print(f"  Warnings: {len(plan['warnings'])}")
    
    if plan['warnings']:
        print("\nWarnings:")
        for warning in plan['warnings']:
            print(f"  - {warning}")
    
    if not args.auto and not args.dry_run:
        response = input("\nProceed with integration? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return
    
    # Integrate files
    integrated = 0
    for file_info in plan['files']:
        source = Path(file_info['source'])
        target = Path(file_info['target'])
        
        if integrate_file(source, target, dry_run=args.dry_run):
            integrated += 1
    
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Integrated {integrated} files.")

if __name__ == "__main__":
    main()
```

---

## Integration Workflow Enhancement

### Update `runner.py` to Support Integration

Add integration hook after code generation:

```python
def run_features(
    features: List[Feature],
    output_dir: Optional[Path] = None,
    verbose: bool = True,
    stop_on_error: bool = False,
    skip_existing: bool = True,
    force: bool = False,
    auto_integrate: bool = False,  # NEW
    integration_mode: str = "review",  # NEW: "auto", "review", "manual"
) -> List[WorkflowResult]:
    """Run Lead Contractor workflow with optional auto-integration."""
    # ... existing code ...
    
    result = run_workflow(feature, verbose)
    results.append(result)
    save_result(result, feature, output_dir)
    
    # NEW: Auto-integration hook
    if auto_integrate and result.success:
        integration_result = integrate_code(result, feature, dry_run=False)
        if verbose:
            print(f"Integration: {integration_result.status}")
    
    # ... rest of code ...
```

---

## Backlog Processing Strategy

### Step 1: Audit Backlog
```bash
python3 scripts/lead_contractor/integrate_backlog.py --list
```

### Step 2: Review Integration Plan
```bash
python3 scripts/lead_contractor/integrate_backlog.py --dry-run
```

### Step 3: Batch Integration by Category
- Graph features → `src/contextcore/graph/`
- A2A features → `src/contextcore/agent/`
- TUI features → `src/contextcore/tui/`
- Install tracking → `scripts/`

### Step 4: Verify Integration
- Run tests
- Check imports
- Update `__init__.py` files
- Commit changes

---

## Safety Measures

1. **Backup Existing Files**: Always backup before overwriting
2. **Dry-Run Mode**: Preview changes before applying
3. **Review Mode**: Show diffs and require approval
4. **Integration Tracking**: Mark files as integrated to prevent duplicates
5. **Rollback Support**: Keep backups for easy rollback

---

## Next Steps

1. ✅ Create backlog integration script
2. ✅ Test on small subset of generated files
3. ✅ Enhance workflow runner with integration hooks
4. ✅ Update feature definitions with target paths
5. ✅ Document integration process in CLAUDE.md

---

## Success Metrics

- **Backlog Reduction**: Process 61+ files → 0 pending
- **Time Savings**: Reduce manual integration time by 80%
- **Error Reduction**: Automated path inference reduces mistakes
- **Workflow Efficiency**: New code integrates automatically
