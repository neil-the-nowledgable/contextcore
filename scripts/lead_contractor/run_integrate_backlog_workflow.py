#!/usr/bin/env python3
"""
Beaver (startd8) workflow for integrating backlog and completing the full cycle.

This workflow:
1. Runs lead_contractor integrate backlog
2. Reviews integrated files
3. Updates imports/exports as needed
4. Runs tests (python3 -m pytest) and fixes errors
5. Commits changes once successful

Usage:
    python3 scripts/lead_contractor/run_integrate_backlog_workflow.py
    python3 scripts/lead_contractor/run_integrate_backlog_workflow.py --feature graph_schema
    python3 scripts/lead_contractor/run_integrate_backlog_workflow.py --dry-run
    python3 scripts/lead_contractor/run_integrate_backlog_workflow.py --skip-tests
    python3 scripts/lead_contractor/run_integrate_backlog_workflow.py --no-commit
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import integrate_backlog functions
from scripts.lead_contractor.integrate_backlog import (
    scan_backlog,
    generate_integration_plan,
    integrate_file,
    infer_target_path,
    GeneratedFile,
)


def review_integrated_files(plan: Dict) -> List[Dict]:
    """
    Review integrated files for common issues.
    
    Returns:
        List of issues found with file paths and descriptions
    """
    issues = []
    
    for item in plan.get('files', []):
        target_path = Path(item['target'])
        
        if not target_path.exists():
            continue
            
        try:
            with open(target_path, 'r') as f:
                content = f.read()
            
            # Check for common issues
            file_issues = []
            
            # Check for missing imports
            if 'import' not in content and len(content) > 100:
                file_issues.append("No imports found - may need imports")
            
            # Check for syntax errors (basic check)
            if content.count('(') != content.count(')'):
                file_issues.append("Unmatched parentheses")
            if content.count('[') != content.count(']'):
                file_issues.append("Unmatched brackets")
            if content.count('{') != content.count('}'):
                file_issues.append("Unmatched braces")
            
            # Check for TODO/FIXME comments
            if 'TODO' in content or 'FIXME' in content:
                file_issues.append("Contains TODO/FIXME comments")
            
            if file_issues:
                issues.append({
                    'file': str(target_path.relative_to(PROJECT_ROOT)),
                    'issues': file_issues
                })
                
        except Exception as e:
            issues.append({
                'file': str(target_path.relative_to(PROJECT_ROOT)),
                'issues': [f"Error reading file: {e}"]
            })
    
    return issues


def update_imports_exports(plan: Dict, dry_run: bool = False) -> Dict:
    """
    Update imports/exports in integrated files.
    
    Returns:
        Dict with update statistics
    """
    stats = {
        'files_updated': 0,
        'imports_added': 0,
        'exports_updated': 0,
        'errors': []
    }
    
    for item in plan.get('files', []):
        target_path = Path(item['target'])
        
        if not target_path.exists():
            continue
        
        # Only process Python files for now
        if target_path.suffix != '.py':
            continue
        
        try:
            with open(target_path, 'r') as f:
                content = f.read()
            
            original_content = content
            updated = False
            
            # Check if file needs __all__ export list
            if '__all__' not in content and 'def ' in content or 'class ' in content:
                # Extract public definitions
                public_defs = []
                for match in re.finditer(r'^(def|class)\s+([A-Za-z_][A-Za-z0-9_]*)', content, re.MULTILINE):
                    if not match.group(2).startswith('_'):
                        public_defs.append(match.group(2))
                
                if public_defs and '__init__.py' not in str(target_path):
                    # Add __all__ after imports
                    import_end = content.find('\n\n')
                    if import_end > 0:
                        __all__ = f"\n__all__ = {public_defs}\n"
                        content = content[:import_end] + __all__ + content[import_end:]
                        updated = True
                        stats['exports_updated'] += 1
            
            # Check for common missing imports based on usage
            missing_imports = []
            
            # Check for Path usage
            if 'Path(' in content and 'from pathlib import Path' not in content and 'import Path' not in content:
                missing_imports.append('from pathlib import Path')
            
            # Check for json usage
            if 'json.' in content and 'import json' not in content:
                missing_imports.append('import json')
            
            # Check for typing usage
            if re.search(r':\s*(List|Dict|Optional|Union|Any)\[', content) and 'from typing import' not in content:
                missing_imports.append('from typing import List, Dict, Optional, Union, Any')
            
            if missing_imports:
                # Add imports at the top after existing imports
                import_section_end = 0
                for line_num, line in enumerate(content.split('\n')):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_section_end = line_num + 1
                    elif line.strip() and import_section_end > 0:
                        break
                
                if import_section_end > 0:
                    lines = content.split('\n')
                    new_imports = '\n'.join(missing_imports)
                    lines.insert(import_section_end, new_imports)
                    content = '\n'.join(lines)
                    updated = True
                    stats['imports_added'] += len(missing_imports)
            
            if updated and not dry_run:
                with open(target_path, 'w') as f:
                    f.write(content)
                stats['files_updated'] += 1
                print(f"  ✓ Updated imports/exports: {target_path.relative_to(PROJECT_ROOT)}")
            elif updated and dry_run:
                print(f"  [DRY RUN] Would update imports/exports: {target_path.relative_to(PROJECT_ROOT)}")
                
        except Exception as e:
            stats['errors'].append(f"{target_path}: {e}")
    
    return stats


def run_tests(dry_run: bool = False, max_attempts: int = 3) -> Dict:
    """
    Run pytest and attempt to fix errors.
    
    Returns:
        Dict with test results and fix attempts
    """
    result = {
        'success': False,
        'attempts': 0,
        'errors': [],
        'fixed': []
    }
    
    if dry_run:
        print("  [DRY RUN] Would run: python3 -m pytest")
        return result
    
    for attempt in range(1, max_attempts + 1):
        result['attempts'] = attempt
        print(f"\n  Running tests (attempt {attempt}/{max_attempts})...")
        
        # Run pytest
        test_result = subprocess.run(
            ['python3', '-m', 'pytest', '-v', '--tb=short'],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        if test_result.returncode == 0:
            print("  ✓ All tests passed!")
            result['success'] = True
            return result
        
        # Parse errors
        error_output = test_result.stderr + test_result.stdout
        result['errors'].append(error_output)
        
        # Try to fix common issues
        fixes_applied = False
        
        # Extract file paths from error messages
        error_files = set()
        for line in error_output.split('\n'):
            # Look for file paths in errors
            match = re.search(r'([a-zA-Z0-9_/]+\.py):(\d+)', line)
            if match:
                error_files.add(match.group(1))
        
        # Try to fix import errors
        for file_path_str in error_files:
            file_path = PROJECT_ROOT / file_path_str
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Fix common import issues
                    if 'ImportError' in error_output or 'ModuleNotFoundError' in error_output:
                        # Try to add missing imports
                        # This is a simplified fix - in practice, you'd need more sophisticated analysis
                        if 'from contextcore' in error_output and 'from contextcore' not in content:
                            # This is too simplistic, but demonstrates the pattern
                            pass
                    
                    # Fix syntax errors if detected
                    if 'SyntaxError' in error_output:
                        # Basic syntax fixes
                        # Remove trailing commas in function calls
                        content = re.sub(r',\s*\)', ')', content)
                        # Fix common indentation issues
                        # (would need more sophisticated parsing)
                        
                        with open(file_path, 'w') as f:
                            f.write(content)
                        fixes_applied = True
                        result['fixed'].append(str(file_path.relative_to(PROJECT_ROOT)))
                        
                except Exception as e:
                    result['errors'].append(f"Error fixing {file_path}: {e}")
        
        if not fixes_applied:
            print(f"  ✗ Tests failed and no automatic fixes could be applied")
            print(f"  Error output:\n{error_output[:500]}...")
            break
        
        print(f"  Applied fixes, retrying tests...")
    
    return result


def commit_changes(plan: Dict, message: Optional[str] = None, dry_run: bool = False) -> bool:
    """
    Commit integrated changes to git.
    
    Returns:
        True if commit successful, False otherwise
    """
    if dry_run:
        print("  [DRY RUN] Would commit changes")
        return True
    
    # Check if we're in a git repo
    git_check = subprocess.run(
        ['git', 'rev-parse', '--git-dir'],
        capture_output=True,
        cwd=PROJECT_ROOT
    )
    
    if git_check.returncode != 0:
        print("  ⚠️  Not in a git repository, skipping commit")
        return False
    
    # Check if there are changes to commit
    status_check = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    
    if not status_check.stdout.strip():
        print("  ✓ No changes to commit")
        return True
    
    # Stage all changes
    subprocess.run(['git', 'add', '-A'], cwd=PROJECT_ROOT)
    
    # Generate commit message
    if not message:
        files_count = len(plan.get('files', []))
        message = f"Integrate backlog: {files_count} file(s) integrated"
    
    # Commit
    commit_result = subprocess.run(
        ['git', 'commit', '-m', message],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    
    if commit_result.returncode == 0:
        print(f"  ✓ Committed changes: {message}")
        return True
    else:
        print(f"  ✗ Failed to commit: {commit_result.stderr}")
        return False


def main():
    """Main workflow execution."""
    parser = argparse.ArgumentParser(
        description="Beaver workflow: Integrate backlog and complete full cycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full workflow with all steps
  %(prog)s
  
  # Dry run to preview
  %(prog)s --dry-run
  
  # Skip tests (for faster iteration)
  %(prog)s --skip-tests
  
  # Don't commit (review first)
  %(prog)s --no-commit
  
  # Process specific feature
  %(prog)s --feature graph_schema
        """
    )
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without executing")
    parser.add_argument("--feature", type=str,
                       help="Process specific feature (partial match)")
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip running tests")
    parser.add_argument("--no-commit", action="store_true",
                       help="Don't commit changes")
    parser.add_argument("--auto", action="store_true",
                       help="Auto-integrate without confirmation")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Beaver Workflow: Integrate Backlog")
    print("=" * 70)
    print()
    
    # Step 1: Run integrate backlog
    print("Step 1: Running integrate backlog...")
    print("-" * 70)
    
    # Import and run integrate_backlog logic
    files = scan_backlog()
    
    if not files:
        print("No generated files found.")
        return
    
    print(f"Found {len(files)} generated file(s)")
    
    plan = generate_integration_plan(files, feature_filter=args.feature)
    
    if not plan['files']:
        print("No files to integrate.")
        return
    
    print(f"Files to integrate: {len(plan['files'])}")
    
    if args.dry_run:
        print("\n[DRY RUN MODE - No files will be modified]")
        for item in plan['files']:
            integrate_file(Path(item['source']), Path(item['target']), dry_run=True)
    else:
        if not args.auto:
            response = input("\nProceed with integration? (yes/no): ")
            if response.lower() not in ('yes', 'y'):
                print("Cancelled.")
                return
        
        integrated = 0
        for item in plan['files']:
            if integrate_file(Path(item['source']), Path(item['target']), dry_run=False):
                integrated += 1
        
        print(f"\n✓ Integrated {integrated} file(s)")
    
    # Step 2: Review integrated files
    print("\n" + "=" * 70)
    print("Step 2: Reviewing integrated files...")
    print("-" * 70)
    
    issues = review_integrated_files(plan)
    
    if issues:
        print(f"Found {len(issues)} file(s) with potential issues:")
        for issue in issues:
            print(f"  • {issue['file']}")
            for item in issue['issues']:
                print(f"    - {item}")
    else:
        print("✓ No issues found in integrated files")
    
    # Step 3: Update imports/exports
    print("\n" + "=" * 70)
    print("Step 3: Updating imports/exports...")
    print("-" * 70)
    
    import_stats = update_imports_exports(plan, dry_run=args.dry_run)
    
    if import_stats['files_updated'] > 0:
        print(f"✓ Updated {import_stats['files_updated']} file(s)")
        print(f"  - Added {import_stats['imports_added']} import(s)")
        print(f"  - Updated {import_stats['exports_updated']} export(s)")
    else:
        print("✓ No import/export updates needed")
    
    if import_stats['errors']:
        print(f"\n⚠️  {len(import_stats['errors'])} error(s) during import updates:")
        for error in import_stats['errors']:
            print(f"  - {error}")
    
    # Step 4: Run tests
    if not args.skip_tests:
        print("\n" + "=" * 70)
        print("Step 4: Running tests...")
        print("-" * 70)
        
        test_result = run_tests(dry_run=args.dry_run)
        
        if test_result['success']:
            print("✓ All tests passed!")
        else:
            print(f"✗ Tests failed after {test_result['attempts']} attempt(s)")
            if test_result['fixed']:
                print(f"  Fixed {len(test_result['fixed'])} file(s):")
                for fixed_file in test_result['fixed']:
                    print(f"    - {fixed_file}")
            
            if not args.dry_run:
                print("\n⚠️  Some tests failed. Please review and fix manually.")
                print("  You can run: python3 -m pytest -v")
                if not args.no_commit:
                    response = input("\nCommit changes anyway? (yes/no): ")
                    if response.lower() not in ('yes', 'y'):
                        print("Skipping commit due to test failures.")
                        return
    else:
        print("\n" + "=" * 70)
        print("Step 4: Skipping tests (--skip-tests)")
        print("-" * 70)
    
    # Step 5: Commit changes
    if not args.no_commit:
        print("\n" + "=" * 70)
        print("Step 5: Committing changes...")
        print("-" * 70)
        
        commit_success = commit_changes(plan, dry_run=args.dry_run)
        
        if commit_success:
            print("✓ Workflow completed successfully!")
        else:
            print("✗ Failed to commit changes")
    else:
        print("\n" + "=" * 70)
        print("Step 5: Skipping commit (--no-commit)")
        print("-" * 70)
        print("✓ Workflow completed (changes not committed)")
    
    print("\n" + "=" * 70)
    print("Workflow Summary")
    print("=" * 70)
    print(f"  Files integrated: {len(plan['files'])}")
    print(f"  Files reviewed: {len(plan['files'])}")
    print(f"  Import/export updates: {import_stats['files_updated']}")
    if not args.skip_tests:
        print(f"  Tests: {'PASSED' if test_result.get('success') else 'FAILED'}")
    print(f"  Commit: {'YES' if not args.no_commit and not args.dry_run else 'SKIPPED'}")


if __name__ == "__main__":
    main()
