"""
Workflow runner utilities for Lead Contractor.
"""

import json
import re
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import (
    LEAD_AGENT,
    DRAFTER_AGENT,
    MAX_ITERATIONS,
    PASS_THRESHOLD,
    OUTPUT_DIR,
    PYTHON_CONTEXT,
    TYPESCRIPT_CONTEXT,
    PYTHON_INTEGRATION,
    TYPESCRIPT_INTEGRATION,
)


@dataclass
class Feature:
    """A feature to be implemented by the Lead Contractor workflow."""
    task: str
    name: str
    is_typescript: bool = False
    output_subdir: Optional[str] = None

    @property
    def context(self) -> Dict[str, str]:
        return TYPESCRIPT_CONTEXT if self.is_typescript else PYTHON_CONTEXT

    @property
    def integration_instructions(self) -> str:
        return TYPESCRIPT_INTEGRATION if self.is_typescript else PYTHON_INTEGRATION

    @property
    def file_extension(self) -> str:
        return ".ts" if self.is_typescript else ".py"


@dataclass
class WorkflowResult:
    """Result from a Lead Contractor workflow run."""
    feature_name: str
    success: bool
    implementation: str
    summary: Dict[str, Any]
    error: Optional[str]
    total_cost: float
    iterations: int


def run_workflow(feature: Feature, verbose: bool = True) -> WorkflowResult:
    """
    Run the Lead Contractor workflow for a single feature.

    Args:
        feature: The feature to implement
        verbose: Whether to print progress

    Returns:
        WorkflowResult with implementation and metrics
    """
    try:
        from startd8.workflows.builtin.lead_contractor_workflow import LeadContractorWorkflow
    except ImportError:
        print("Error: startd8 SDK not found. Please ensure it's installed.")
        print("Expected path: /Users/neilyashinsky/Documents/dev/startd8-sdk/src")
        return WorkflowResult(
            feature_name=feature.name,
            success=False,
            implementation="",
            summary={},
            error="startd8 SDK not found",
            total_cost=0,
            iterations=0,
        )

    if verbose:
        print(f"\n{'='*60}")
        print(f"Running Lead Contractor: {feature.name}")
        print(f"Language: {'TypeScript' if feature.is_typescript else 'Python'}")
        print(f"{'='*60}\n")

    workflow = LeadContractorWorkflow()

    config = {
        "task_description": feature.task,
        "context": feature.context,
        "lead_agent": LEAD_AGENT,
        "drafter_agent": DRAFTER_AGENT,
        "max_iterations": MAX_ITERATIONS,
        "pass_threshold": PASS_THRESHOLD,
        "integration_instructions": feature.integration_instructions,
    }

    result = workflow.run(config=config)

    return WorkflowResult(
        feature_name=feature.name,
        success=result.success,
        implementation=result.output.get("final_implementation", ""),
        summary=result.output.get("summary", {}),
        error=result.error,
        total_cost=result.metrics.total_cost if result.metrics else 0,
        iterations=result.metadata.get("total_iterations", 0),
    )


def extract_code(text: str, language: str = "python") -> str:
    """Extract code from markdown code blocks."""
    # Try language-specific blocks
    for lang in ([language] if language != "typescript" else ["typescript", "ts"]):
        pattern = rf'```{lang}\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return "\n\n".join(matches)

    # Try generic blocks
    pattern = r'```\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return "\n\n".join(matches)

    return text


def save_result(result: WorkflowResult, feature: Feature, output_dir: Optional[Path] = None):
    """Save workflow result to files."""
    base_dir = output_dir or OUTPUT_DIR
    if feature.output_subdir:
        base_dir = base_dir / feature.output_subdir
    base_dir.mkdir(parents=True, exist_ok=True)

    slug = feature.name.replace(" ", "_").lower()

    # Save metadata as JSON
    meta_file = base_dir / f"{slug}_result.json"
    with open(meta_file, "w") as f:
        json.dump({
            "feature": result.feature_name,
            "success": result.success,
            "summary": result.summary,
            "error": result.error,
            "total_cost": result.total_cost,
            "iterations": result.iterations,
        }, f, indent=2)

    # Save implementation code
    lang = "typescript" if feature.is_typescript else "python"
    code = extract_code(result.implementation, lang)
    code_file = base_dir / f"{slug}_code{feature.file_extension}"
    with open(code_file, "w") as f:
        f.write(code)

    print(f"Saved: {meta_file}")
    print(f"Saved: {code_file}")

    return meta_file, code_file


def run_features(
    features: List[Feature],
    output_dir: Optional[Path] = None,
    verbose: bool = True,
    stop_on_error: bool = False,
) -> List[WorkflowResult]:
    """
    Run Lead Contractor workflow for multiple features.

    Args:
        features: List of features to implement
        output_dir: Output directory for generated code
        verbose: Whether to print progress
        stop_on_error: Whether to stop on first error

    Returns:
        List of WorkflowResults
    """
    results = []

    for i, feature in enumerate(features, 1):
        if verbose:
            print(f"\n[{i}/{len(features)}] Processing {feature.name}")

        try:
            result = run_workflow(feature, verbose)
            results.append(result)
            save_result(result, feature, output_dir)

            if verbose:
                print(f"\nResult: {'SUCCESS' if result.success else 'FAILED'}")
                print(f"  Iterations: {result.iterations}")
                print(f"  Cost: ${result.total_cost:.4f}")
                if result.error:
                    print(f"  Error: {result.error}")

            if not result.success and stop_on_error:
                print("\nStopping due to error (--stop-on-error)")
                break

        except Exception as e:
            print(f"\nException running {feature.name}: {e}")
            traceback.print_exc()
            if stop_on_error:
                break

    # Print summary
    if verbose and len(results) > 1:
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total features: {len(results)}")
        print(f"Successful: {sum(1 for r in results if r.success)}")
        print(f"Failed: {sum(1 for r in results if not r.success)}")
        print(f"Total cost: ${sum(r.total_cost for r in results):.4f}")

    return results
