#!/usr/bin/env python3
"""
Process backlog of generated Lead Contractor code.

Scans generated/ directories, identifies unintegrated code,
and provides integration assistance.

Usage:
    # List all pending integrations
    python3 scripts/lead_contractor/integrate_backlog.py --list
    
    # Preview integration plan (dry-run)
    python3 scripts/lead_contractor/integrate_backlog.py --dry-run
    
    # Integrate all files (with confirmation)
    python3 scripts/lead_contractor/integrate_backlog.py
    
    # Integrate specific feature
    python3 scripts/lead_contractor/integrate_backlog.py --feature graph_schema
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class GeneratedFile:
    """Represents a generated code file."""
    path: Path
    feature_name: str
    result_file: Path
    target_path: Optional[Path] = None
    integrated: bool = False
    metadata: Dict = field(default_factory=dict)


def scan_backlog() -> List[GeneratedFile]:
    """Scan generated/ directories for unintegrated code."""
    generated_files = []
    generated_dir = PROJECT_ROOT / "generated"
    
    if not generated_dir.exists():
        print(f"Warning: {generated_dir} does not exist")
        print(f"  PROJECT_ROOT: {PROJECT_ROOT}")
        print(f"  Generated dir: {generated_dir}")
        return []
    
    # Find all *_code.py and *_code.ts files
    code_files = list(generated_dir.rglob("*_code.*"))
    if not code_files:
        print(f"Debug: No *_code.* files found in {generated_dir}")
        print(f"  Generated dir exists: {generated_dir.exists()}")
        # Try alternative search
        if generated_dir.exists():
            all_files = list(generated_dir.rglob("*"))
            print(f"  Total files in generated/: {len(all_files)}")
            code_like = [f for f in all_files if "_code" in f.name]
            print(f"  Files with '_code' in name: {len(code_like)}")
        return []
    
    print(f"Debug: Found {len(code_files)} code files")
    
    for code_file in code_files:
        # Skip if already in source tree (likely integrated)
        if "src/" in str(code_file) or "extensions/" in str(code_file):
            continue
            
        # Find corresponding result file
        # Pattern: feature_3_1a_graph_schema_code.py -> feature_3_1a_graph_schema_result.json
        result_file = code_file.parent / code_file.name.replace("_code.", "_result.")
        
        # If result file doesn't exist, try .json extension
        if not result_file.exists() and result_file.suffix != ".json":
            result_file = result_file.with_suffix(".json")
        
        if result_file.exists():
            try:
                with open(result_file) as f:
                    result = json.load(f)
                    feature_name = result.get("feature", "unknown")
                    
                    generated_files.append(GeneratedFile(
                        path=code_file,
                        feature_name=feature_name,
                        result_file=result_file,
                        integrated=False,
                        metadata=result
                    ))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not read {result_file}: {e}")
    
    return generated_files


def infer_target_path(generated_file: GeneratedFile) -> Optional[Path]:
    """Infer target path from feature name and file content."""
    feature = generated_file.feature_name.lower()
    file_name = generated_file.path.name
    
    # Remove _code suffix and get base name
    base_name = file_name.replace("_code.py", ".py").replace("_code.ts", ".ts")
    
    # Heuristics based on feature name patterns
    if "graph" in feature:
        if "schema" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "graph" / "schema.py"
        elif "builder" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "graph" / "builder.py"
        elif "queries" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "graph" / "queries.py"
        elif "cli" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "graph" / "cli.py"
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "graph" / base_name
    
    elif "a2a" in feature or "adapter" in feature:
        if "discovery" in feature:
            # Discovery features go to src/contextcore/discovery/, not agent/
            if "agentcard" in feature:
                return PROJECT_ROOT / "src" / "contextcore" / "discovery" / "agentcard.py"
            elif "endpoint" in feature:
                return PROJECT_ROOT / "src" / "contextcore" / "discovery" / "endpoint.py"
            elif "client" in feature:
                return PROJECT_ROOT / "src" / "contextcore" / "discovery" / "client.py"
            elif "package" in feature:
                return PROJECT_ROOT / "src" / "contextcore" / "discovery" / "__init__.py"
            else:
                return PROJECT_ROOT / "src" / "contextcore" / "discovery" / base_name
        elif "adapter" in feature:
            if "task" in feature:
                return PROJECT_ROOT / "src" / "contextcore" / "agent" / "a2a_adapter.py"
            elif "message" in feature:
                return PROJECT_ROOT / "src" / "contextcore" / "agent" / "a2a_adapter.py"
            elif "server" in feature or "client" in feature:
                return PROJECT_ROOT / "src" / "contextcore" / "agent" / "a2a_adapter.py"
            else:
                return PROJECT_ROOT / "src" / "contextcore" / "agent" / "a2a_adapter.py"
        elif "state" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "handoff.py"
        elif "parts" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "parts.py"
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / base_name
    
    elif "tui" in feature:
        # TUI files may have specific paths in the content
        return PROJECT_ROOT / "src" / "contextcore" / "tui" / base_name
    
    elif "install" in feature or "tracking" in feature:
        if file_name.endswith(".sh"):
            return PROJECT_ROOT / "scripts" / base_name
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "install" / base_name
    
    elif "slo" in feature or "test" in feature:
        return PROJECT_ROOT / "src" / "contextcore" / "generators" / "slo_tests.py"
    
    elif "pr" in feature and "review" in feature:
        return PROJECT_ROOT / "src" / "contextcore" / "integrations" / "github_review.py"
    
    elif "contract" in feature and "drift" in feature:
        return PROJECT_ROOT / "src" / "contextcore" / "integrations" / "contract_drift.py"
    
    elif "api" in feature:
        if "insights" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "api" / "insights.py"
        elif "handoffs" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "api" / "handoffs.py"
        elif "skills" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "api" / "skills.py"
        elif "package" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "api" / "__init__.py"
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "api" / base_name
    
    elif "discovery" in feature:
        if "agentcard" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "discovery" / "agentcard.py"
        elif "endpoint" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "discovery" / "endpoint.py"
        elif "client" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "discovery" / "client.py"
        elif "package" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "discovery" / "__init__.py"
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "discovery" / base_name
    
    elif "state" in feature:
        if "input" in feature or "request" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "handoff.py"
        elif "enhanced" in feature or "status" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "handoff.py"
        elif "events" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "events.py"
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "handoff.py"
    
    elif "parts" in feature:
        if "message" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "parts.py"
        elif "part" in feature and "model" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "parts.py"
        elif "artifact" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "parts.py"
        elif "models" in feature and "package" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "parts.py"
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "agent" / "parts.py"
    
    elif "otel" in feature or "unified" in feature:
        if "conversation" in feature or "conversationid" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "compat" / "otel_genai.py"
        elif "operation" in feature or "operationname" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "compat" / "operations.py"
        elif "tool" in feature and "mapping" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "compat" / "otel_genai.py"
        elif "provider" in feature or "model" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "tracing" / "insight_emitter.py"
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "compat" / base_name
    
    elif "foundation" in feature:
        if "gap" in feature or "analysis" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "compat" / "otel_genai.py"
        elif "dual" in feature or "emit" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "compat" / "otel_genai.py"
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "compat" / base_name
    
    elif "docs" in feature or "documentation" in feature:
        # Documentation updates might be markdown files or code
        if file_name.endswith(".md"):
            return PROJECT_ROOT / "docs" / base_name
        else:
            # Code that generates docs might go in docs/ or src/
            return PROJECT_ROOT / "docs" / base_name
    
    elif "learning" in feature:
        if "models" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "learning" / "models.py"
        elif "emitter" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "learning" / "emitter.py"
        elif "retriever" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "learning" / "retriever.py"
        elif "loop" in feature:
            return PROJECT_ROOT / "src" / "contextcore" / "learning" / "loop.py"
        else:
            return PROJECT_ROOT / "src" / "contextcore" / "learning" / base_name
    
    elif "vscode" in feature or "assembly" in feature:
        # VSCode extension files
        if "package" in feature:
            return PROJECT_ROOT / "extensions" / "vscode" / "package.json"
        elif file_name.endswith(".ts"):
            # Try to infer from file content or use generic location
            return PROJECT_ROOT / "extensions" / "vscode" / "src" / base_name
        else:
            return PROJECT_ROOT / "extensions" / "vscode" / base_name
    
    # Default: try to infer from file content
    try:
        with open(generated_file.path, 'r') as f:
            content = f.read(500)  # Read first 500 chars
            # Look for module path hints
            if "src/contextcore" in content:
                # Try to extract path hints
                import re
                path_match = re.search(r'src/contextcore/([^\s"\']+)', content)
                if path_match:
                    rel_path = path_match.group(1).split()[0]
                    return PROJECT_ROOT / "src" / "contextcore" / rel_path
    except IOError:
        pass
    
    return None


def check_if_integrated(generated_file: GeneratedFile, target_path: Path) -> bool:
    """Check if file has already been integrated."""
    if not target_path.exists():
        return False
    
    # Compare file sizes and modification times as heuristic
    # (Not perfect, but good enough for detection)
    try:
        source_stat = generated_file.path.stat()
        target_stat = target_path.stat()
        
        # If target is newer and similar size, likely integrated
        if target_stat.st_mtime > source_stat.st_mtime:
            size_diff = abs(source_stat.st_size - target_stat.st_size)
            if size_diff < 100:  # Within 100 bytes
                return True
    except OSError:
        pass
    
    return False


def generate_integration_plan(
    files: List[GeneratedFile],
    feature_filter: Optional[str] = None
) -> Dict:
    """Generate integration plan with target paths."""
    plan = {
        "files": [],
        "warnings": [],
        "requires_review": [],
        "already_integrated": []
    }
    
    for file in files:
        # Filter by feature if specified
        if feature_filter and feature_filter.lower() not in file.feature_name.lower():
            continue
        
        target = infer_target_path(file)
        if target:
            # Check if already integrated
            if check_if_integrated(file, target):
                plan["already_integrated"].append({
                    "source": str(file.path),
                    "target": str(target),
                    "feature": file.feature_name
                })
            else:
                plan["files"].append({
                    "source": str(file.path),
                    "target": str(target),
                    "feature": file.feature_name
                })
        else:
            plan["warnings"].append(f"Could not infer target for {file.path.name} ({file.feature_name})")
            plan["requires_review"].append(file)
    
    return plan


def integrate_file(source: Path, target: Path, dry_run: bool = False) -> bool:
    """Integrate a single file."""
    if dry_run:
        print(f"  [DRY RUN] Would copy {source.name}")
        print(f"    From: {source}")
        print(f"    To:   {target}")
        return True
    
    # Create backup if target exists
    if target.exists():
        backup = target.with_suffix(f"{target.suffix}.backup")
        shutil.copy2(target, backup)
        print(f"  Backed up existing file to {backup.name}")
    
    # Create target directory
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    shutil.copy2(source, target)
    print(f"  ✓ Integrated: {target.relative_to(PROJECT_ROOT)}")
    
    return True


def main():
    """Main integration workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Integrate Lead Contractor generated code into source tree",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all pending integrations
  %(prog)s --list
  
  # Preview integration plan
  %(prog)s --dry-run
  
  # Integrate all files
  %(prog)s
  
  # Integrate specific feature
  %(prog)s --feature graph_schema
        """
    )
    parser.add_argument("--dry-run", action="store_true", 
                       help="Preview changes without integrating")
    parser.add_argument("--feature", type=str, 
                       help="Process specific feature (partial match)")
    parser.add_argument("--list", action="store_true", 
                       help="List all pending integrations")
    parser.add_argument("--auto", action="store_true", 
                       help="Auto-integrate without confirmation (use with caution)")
    
    args = parser.parse_args()
    
    print("Scanning generated/ directories...")
    files = scan_backlog()
    
    if not files:
        print("No generated files found.")
        return
    
    print(f"Found {len(files)} generated file(s)")
    
    if args.list:
        print(f"\n{'='*70}")
        print("Generated Files Inventory")
        print(f"{'='*70}\n")
        
        for f in files:
            target = infer_target_path(f)
            status = "✓" if target and check_if_integrated(f, target) else "?"
            print(f"{status} {f.feature_name}")
            print(f"    File: {f.path.relative_to(PROJECT_ROOT)}")
            if target:
                integrated = check_if_integrated(f, target)
                status_text = " (already integrated)" if integrated else ""
                print(f"    -> {target.relative_to(PROJECT_ROOT)}{status_text}")
            else:
                print(f"    -> [Could not infer target path]")
            print()
        return
    
    # Generate integration plan
    plan = generate_integration_plan(files, feature_filter=args.feature)
    
    print(f"\n{'='*70}")
    print("Integration Plan")
    print(f"{'='*70}")
    print(f"  Files to integrate: {len(plan['files'])}")
    print(f"  Already integrated: {len(plan['already_integrated'])}")
    print(f"  Requires review: {len(plan['requires_review'])}")
    print(f"  Warnings: {len(plan['warnings'])}")
    
    if plan['already_integrated']:
        print(f"\nAlready Integrated ({len(plan['already_integrated'])}):")
        for item in plan['already_integrated']:
            print(f"  ✓ {item['feature']}")
    
    if plan['warnings']:
        print(f"\n⚠️  Warnings ({len(plan['warnings'])}):")
        for warning in plan['warnings']:
            print(f"  - {warning}")
    
    if plan['requires_review']:
        print(f"\n📋 Requires Manual Review ({len(plan['requires_review'])}):")
        for file in plan['requires_review']:
            print(f"  - {file.feature_name}: {file.path.name}")
    
    if not plan['files']:
        print("\nNo files to integrate.")
        return
    
    print(f"\n📦 Files to Integrate ({len(plan['files'])}):")
    for item in plan['files']:
        source_rel = Path(item['source']).relative_to(PROJECT_ROOT)
        target_rel = Path(item['target']).relative_to(PROJECT_ROOT)
        print(f"  • {item['feature']}")
        print(f"    {source_rel} -> {target_rel}")
    
    if args.dry_run:
        print(f"\n{'='*70}")
        print("DRY RUN MODE - No files will be modified")
        print(f"{'='*70}\n")
        for item in plan['files']:
            integrate_file(Path(item['source']), Path(item['target']), dry_run=True)
        return
    
    if not args.auto:
        print(f"\n{'='*70}")
        response = input("Proceed with integration? (yes/no): ")
        if response.lower() not in ('yes', 'y'):
            print("Cancelled.")
            return
    
    # Integrate files
    print(f"\n{'='*70}")
    print("Integrating Files")
    print(f"{'='*70}\n")
    
    integrated = 0
    failed = 0
    
    for item in plan['files']:
        source = Path(item['source'])
        target = Path(item['target'])
        
        try:
            if integrate_file(source, target, dry_run=False):
                integrated += 1
        except Exception as e:
            print(f"  ✗ Failed to integrate {source.name}: {e}")
            failed += 1
    
    print(f"\n{'='*70}")
    print("Integration Complete")
    print(f"{'='*70}")
    print(f"  ✓ Integrated: {integrated}")
    if failed > 0:
        print(f"  ✗ Failed: {failed}")
    print(f"\nNext steps:")
    print(f"  1. Review integrated files")
    print(f"  2. Update imports/exports as needed")
    print(f"  3. Run tests: python3 -m pytest")
    print(f"  4. Commit changes")


if __name__ == "__main__":
    main()
