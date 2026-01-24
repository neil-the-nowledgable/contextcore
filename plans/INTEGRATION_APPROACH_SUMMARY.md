# Lead Contractor Integration Approach Summary

## Problem Statement

The Lead Contractor workflow generates code but **does not automatically integrate it** into the source tree. There's a backlog of **60+ generated code files** waiting for manual integration.

## Solution Overview

I've created a **two-pronged approach**:

1. **Backlog Integration Script** - Process existing generated code
2. **Future Enhancement Plan** - Automate integration for new code

---

## ✅ Immediate Solution: Backlog Integration Script

### Script: `scripts/lead_contractor/integrate_backlog.py`

**Status**: ✅ Created and tested

### Features

- **Scans** all `generated/` directories for unintegrated code
- **Infers target paths** using heuristics based on feature names
- **Generates integration plan** with preview
- **Supports dry-run mode** for safe testing
- **Tracks integration status** to prevent duplicates

### Usage

```bash
# List all pending integrations
python3 scripts/lead_contractor/integrate_backlog.py --list

# Preview integration plan (safe, no changes)
python3 scripts/lead_contractor/integrate_backlog.py --dry-run

# Integrate all files (with confirmation)
python3 scripts/lead_contractor/integrate_backlog.py

# Integrate specific feature
python3 scripts/lead_contractor/integrate_backlog.py --feature graph_schema

# Auto-integrate without confirmation (use with caution)
python3 scripts/lead_contractor/integrate_backlog.py --auto
```

### Current Backlog Status

The script found **60 generated files** including:
- Graph features (schema, builder, queries, CLI)
- A2A features (adapter, discovery, state, parts)
- Learning features (models, emitter, retriever, loop)
- TUI features
- VSCode extension features
- Install tracking features

### Path Inference Heuristics

The script automatically infers target paths:
- `graph_*` → `src/contextcore/graph/`
- `a2a_*` → `src/contextcore/agent/`
- `tui_*` → `src/contextcore/tui/`
- `install_*` → `scripts/` or `src/contextcore/install/`
- `learning_*` → `src/contextcore/learning/`
- `vscode_*` → `extensions/vscode/`

---

## 🔄 Future Enhancement: Automated Integration

### Plan: Enhance `runner.py` with Integration Hooks

**Status**: 📋 Planned (see `plans/LEAD_CONTRACTOR_INTEGRATION_AUTOMATION.md`)

### Proposed Changes

1. **Add integration mode to Feature model**:
```python
@dataclass
class Feature:
    # ... existing fields ...
    integration_mode: str = "review"  # "auto", "review", "manual"
    target_paths: Optional[Dict[str, str]] = None
```

2. **Add integration hook to `run_features()`**:
```python
def run_features(
    # ... existing params ...
    auto_integrate: bool = False,
    integration_mode: str = "review",
) -> List[WorkflowResult]:
    # After code generation:
    if auto_integrate and result.success:
        integration_result = integrate_code(result, feature)
```

3. **Create integration function**:
```python
def integrate_code(
    result: WorkflowResult,
    feature: Feature,
    dry_run: bool = False
) -> IntegrationResult:
    """Integrate generated code into source tree."""
```

---

## 📋 Recommended Workflow

### Phase 1: Process Backlog (Now)

1. **Audit backlog**:
   ```bash
   python3 scripts/lead_contractor/integrate_backlog.py --list
   ```

2. **Review integration plan**:
   ```bash
   python3 scripts/lead_contractor/integrate_backlog.py --dry-run
   ```

3. **Integrate by category** (safer than all at once):
   ```bash
   # Graph features
   python3 scripts/lead_contractor/integrate_backlog.py --feature graph
   
   # A2A features
   python3 scripts/lead_contractor/integrate_backlog.py --feature a2a
   
   # Learning features
   python3 scripts/lead_contractor/integrate_backlog.py --feature learning
   ```

4. **Verify integration**:
   - Review integrated files
   - Update `__init__.py` files as needed
   - Fix imports
   - Run tests: `python3 -m pytest`
   - Commit changes

### Phase 2: Enhance Workflow (Future)

1. Update `Feature` model with integration metadata
2. Add integration hooks to `runner.py`
3. Test with new feature generation
4. Document in `CLAUDE.md`

---

## 🛡️ Safety Measures

The integration script includes:

1. **Backup existing files** - Creates `.backup` files before overwriting
2. **Dry-run mode** - Preview changes without applying
3. **Confirmation prompts** - Requires explicit approval (unless `--auto`)
4. **Integration tracking** - Detects already-integrated files
5. **Path validation** - Verifies target paths before copying

---

## 📊 Success Metrics

- **Backlog Reduction**: 60 files → 0 pending
- **Time Savings**: Reduce manual integration time by 80%
- **Error Reduction**: Automated path inference reduces mistakes
- **Workflow Efficiency**: New code integrates automatically (future)

---

## 📝 Next Steps

1. ✅ **Created backlog integration script**
2. ✅ **Tested script with existing backlog**
3. 📋 **Process backlog in batches** (recommended: by feature category)
4. 📋 **Enhance workflow runner** with integration hooks
5. 📋 **Update feature definitions** with target paths
6. 📋 **Document integration process** in `CLAUDE.md`

---

## Files Created

1. `scripts/lead_contractor/integrate_backlog.py` - Backlog integration script
2. `plans/LEAD_CONTRACTOR_INTEGRATION_AUTOMATION.md` - Detailed technical plan
3. `plans/INTEGRATION_APPROACH_SUMMARY.md` - This summary

---

## Questions or Issues?

- **Path inference not working?** Check the heuristics in `infer_target_path()`
- **File already integrated?** The script detects this and skips
- **Need manual review?** Use `--dry-run` first, then integrate manually
- **Want to customize paths?** Edit the `infer_target_path()` function
