# Code Generation Rules

These rules apply when generating code for multiple features or making changes to the codebase.

## Rule 1: Integrate Immediately

**NEVER** batch multiple features for later integration. Each feature MUST be integrated and validated before starting the next.

```
✅ DO: Feature 1 → Integrate → Validate → Feature 2 → Integrate → Validate
❌ DON'T: Feature 1, Feature 2, Feature 3 → Integrate all → Fix conflicts
```

## Rule 2: Use Prime Contractor for Multiple Features

When generating more than one feature, use the Prime Contractor workflow:

```bash
python3 scripts/prime_contractor/cli.py run --import-backlog
```

This ensures:
- Features are integrated one at a time
- Conflicts are detected early
- Checkpoints validate each integration
- The mainline stays working

## Rule 3: Check for Overlapping Targets

Before generating a feature, check if it targets files modified by previous features:

```bash
python3 scripts/prime_contractor/cli.py status
```

If overlap exists, the Prime Contractor will handle merging appropriately.

## Rule 4: Stop on Failure

If integration or checkpoints fail:
1. STOP immediately
2. Fix the issue
3. Retry the feature
4. Only then proceed to the next feature

```bash
# After fixing the issue
python3 scripts/prime_contractor/cli.py retry feature_id
```

## Rule 5: Commit Atomically

Each feature should be committed separately, not batched:

```bash
# Use auto-commit for atomic commits
python3 scripts/prime_contractor/cli.py run --import-backlog --auto-commit
```

## Anti-Patterns to Avoid

1. **Backlog Accumulation**: Generating many features without integration
2. **Skip Validation**: Proceeding without running checkpoints
3. **Big Bang Integration**: Integrating all features at once
4. **Ignoring Conflicts**: Hoping conflicts will resolve themselves
5. **Context Loss**: Generating features without knowledge of recent changes

## When in Doubt

If unsure whether to use Prime Contractor:
- More than 1 feature? → Use Prime Contractor
- Features might touch same files? → Use Prime Contractor
- Want to avoid manual merging? → Use Prime Contractor

The Prime Contractor is always safer. The only downside is slightly slower processing (one feature at a time), but this is far better than hours of manual conflict resolution.
