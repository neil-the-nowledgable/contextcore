# Debug Install Mode Implementation Plan

**Created**: 2026-01-22
**Status**: Ready for Implementation
**Priority**: High

## Overview

Create a debug mode for `contextcore install verify` that enables step-by-step validation of metrics being generated, with actual verification against Mimir to confirm metrics are received correctly.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Granularity** | Per-category by default, `--step-all` for per-requirement | 5 checkpoints is manageable; 28 steps available for deep debugging |
| **Verification Method** | Display locally AND query Mimir | Confirms end-to-end telemetry pipeline works |
| **User Control** | Interactive prompts with Enter/q | Allows inspection at each step |

---

## Implementation Steps

### Step 1: Create Mimir Query Module

**File**: `src/contextcore/install/mimir_query.py`

This module queries Mimir's Prometheus-compatible API to verify metrics were received.

```python
"""Query Mimir for metric verification in debug mode."""

import os
import time
from typing import Optional
import requests

def _get_mimir_url() -> str:
    """Get Mimir URL from environment or default."""
    return os.environ.get("MIMIR_URL", "http://localhost:9009")

def query_metric(
    metric_name: str,
    labels: dict[str, str],
    mimir_url: Optional[str] = None,
    timeout: float = 5.0
) -> Optional[float]:
    """
    Query Mimir for a specific metric value.

    Args:
        metric_name: Prometheus metric name (e.g., contextcore_install_requirement_status_ratio)
        labels: Label matchers (e.g., {"requirement_id": "grafana_running"})
        mimir_url: Mimir base URL (defaults to MIMIR_URL env var or localhost:9009)
        timeout: Request timeout in seconds

    Returns:
        The metric value if found, None if not found or error
    """
    url = mimir_url or _get_mimir_url()

    # Build PromQL query with label matchers
    label_matchers = ",".join(f'{k}="{v}"' for k, v in labels.items())
    query = f'{metric_name}{{{label_matchers}}}'

    try:
        response = requests.get(
            f"{url}/api/v1/query",
            params={"query": query},
            timeout=timeout
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success" and data.get("data", {}).get("result"):
            # Return the most recent value
            result = data["data"]["result"][0]
            return float(result["value"][1])
        return None
    except Exception:
        return None

def verify_metric_emitted(
    metric_name: str,
    expected_value: float,
    labels: dict[str, str],
    mimir_url: Optional[str] = None,
    tolerance: float = 0.01,
    retry_count: int = 3,
    retry_delay: float = 1.0
) -> tuple[bool, Optional[float], Optional[str]]:
    """
    Verify a metric exists in Mimir with the expected value.

    Args:
        metric_name: Prometheus metric name
        expected_value: Expected metric value
        labels: Label matchers
        mimir_url: Mimir base URL
        tolerance: Acceptable difference between expected and actual
        retry_count: Number of retries if metric not found
        retry_delay: Seconds between retries

    Returns:
        Tuple of (success, actual_value, error_message)
    """
    for attempt in range(retry_count):
        actual = query_metric(metric_name, labels, mimir_url)

        if actual is not None:
            if abs(actual - expected_value) <= tolerance:
                return (True, actual, None)
            else:
                return (False, actual, f"Value mismatch: expected {expected_value}, got {actual}")

        if attempt < retry_count - 1:
            time.sleep(retry_delay)

    return (False, None, "Metric not found in Mimir after retries")

def query_all_install_metrics(
    mimir_url: Optional[str] = None
) -> dict[str, list[dict]]:
    """
    Query all ContextCore installation metrics from Mimir.

    Returns:
        Dict mapping metric names to list of {labels, value} dicts
    """
    url = mimir_url or _get_mimir_url()
    metrics = {}

    metric_names = [
        "contextcore_install_completeness_percent",
        "contextcore_install_requirement_status_ratio",
        "contextcore_install_category_completeness_percent",
        "contextcore_install_verification_duration_milliseconds",
        "contextcore_install_critical_met_ratio",
        "contextcore_install_critical_total_ratio",
    ]

    for metric_name in metric_names:
        try:
            response = requests.get(
                f"{url}/api/v1/query",
                params={"query": metric_name},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success":
                results = []
                for result in data.get("data", {}).get("result", []):
                    results.append({
                        "labels": result.get("metric", {}),
                        "value": float(result["value"][1])
                    })
                metrics[metric_name] = results
        except Exception:
            metrics[metric_name] = []

    return metrics
```

---

### Step 2: Create Debug Display Module

**File**: `src/contextcore/install/debug_display.py`

Rich-formatted output for debug mode checkpoints.

```python
"""Debug display utilities for installation verification."""

import sys
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

@dataclass
class MetricComparison:
    """Comparison between local and Mimir metric values."""
    metric_name: str
    labels: dict[str, str]
    local_value: float
    mimir_value: Optional[float]
    match: bool
    error: Optional[str] = None

def display_category_checkpoint(
    category_name: str,
    category_index: int,
    total_categories: int,
    requirements_results: list,  # List of RequirementResult
    category_completeness: float
) -> None:
    """Display a category checkpoint with all requirement results."""

    # Header
    console.print()
    console.print(Panel(
        f"[bold cyan]CATEGORY CHECKPOINT: {category_name.upper()} ({category_index}/{total_categories})[/]",
        style="cyan"
    ))

    # Requirements table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Status", width=8)
    table.add_column("Requirement ID", min_width=25)
    table.add_column("Result", width=10)
    table.add_column("Duration", width=10)
    table.add_column("Error", max_width=40)

    for result in requirements_results:
        status_icon = "✓" if result.passed else ("⊘" if result.status.value == "skipped" else "✗")
        status_color = "green" if result.passed else ("yellow" if result.status.value == "skipped" else "red")

        table.add_row(
            Text(status_icon, style=status_color),
            result.requirement.id,
            Text(result.status.value.upper(), style=status_color),
            f"{result.duration_ms:.0f}ms",
            result.error or ""
        )

    console.print(table)
    console.print(f"\n[bold]Category Summary:[/] Passed: {category_completeness:.1f}%\n")

def display_requirement_checkpoint(
    requirement_id: str,
    requirement_index: int,
    total_requirements: int,
    result,  # RequirementResult
) -> None:
    """Display a single requirement checkpoint."""

    status_icon = "✓" if result.passed else ("⊘" if result.status.value == "skipped" else "✗")
    status_color = "green" if result.passed else ("yellow" if result.status.value == "skipped" else "red")

    console.print()
    console.print(Panel(
        f"[bold {status_color}]REQUIREMENT: {requirement_id} ({requirement_index}/{total_requirements}) - {result.status.value.upper()}[/]",
        style=status_color
    ))

    console.print(f"  [dim]Category:[/] {result.requirement.category.value}")
    console.print(f"  [dim]Critical:[/] {'Yes' if result.requirement.critical else 'No'}")
    console.print(f"  [dim]Duration:[/] {result.duration_ms:.0f}ms")
    if result.error:
        console.print(f"  [red]Error:[/] {result.error}")
    console.print()

def display_metrics_local(metrics: dict[str, float]) -> None:
    """Display locally emitted metrics."""

    console.print(Panel("[bold yellow]METRICS EMITTED (Local)[/]", style="yellow"))

    for metric_key, value in metrics.items():
        console.print(f"  {metric_key} = [cyan]{value}[/]")
    console.print()

def display_metric_comparison(comparisons: list[MetricComparison]) -> None:
    """Display side-by-side comparison of local vs Mimir values."""

    console.print(Panel("[bold magenta]MIMIR VERIFICATION[/]", style="magenta"))

    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric", min_width=50)
    table.add_column("Local", width=10, justify="right")
    table.add_column("Mimir", width=10, justify="right")
    table.add_column("Match", width=8)

    all_match = True
    for comp in comparisons:
        # Truncate metric name for display
        metric_display = comp.metric_name
        if comp.labels:
            label_str = ",".join(f'{k}="{v}"' for k, v in list(comp.labels.items())[:2])
            metric_display = f"{comp.metric_name}{{{label_str}...}}"
        if len(metric_display) > 50:
            metric_display = metric_display[:47] + "..."

        mimir_str = f"{comp.mimir_value}" if comp.mimir_value is not None else "NOT FOUND"
        match_icon = "✓" if comp.match else "✗"
        match_color = "green" if comp.match else "red"

        table.add_row(
            metric_display,
            f"{comp.local_value}",
            mimir_str,
            Text(match_icon, style=match_color)
        )

        if not comp.match:
            all_match = False

    console.print(table)

    if all_match:
        console.print("\n[bold green]All metrics verified! ✓[/]\n")
    else:
        console.print("\n[bold red]Some metrics did not match! ✗[/]\n")

def prompt_continue() -> bool:
    """
    Prompt user to continue or quit.

    Returns:
        True to continue, False to abort
    """
    console.print("[dim]Press Enter to continue, or 'q' to quit...[/]", end="")
    try:
        user_input = input()
        return user_input.lower() != 'q'
    except (EOFError, KeyboardInterrupt):
        return False
```

---

### Step 3: Add Debug Checkpoint to Verifier

**File**: `src/contextcore/install/verifier.py`

Add `DebugCheckpoint` dataclass and `verify_debug()` method.

```python
# Add to imports
from typing import Callable, Optional
from dataclasses import dataclass, field

# Add new dataclass after existing ones
@dataclass
class DebugCheckpoint:
    """Data passed to debug callback at each checkpoint."""

    checkpoint_type: str  # "requirement" or "category"
    checkpoint_index: int
    total_checkpoints: int

    # For requirement checkpoints
    requirement_result: Optional[RequirementResult] = None

    # For category checkpoints
    category: Optional[RequirementCategory] = None
    category_results: list[RequirementResult] = field(default_factory=list)
    category_completeness: float = 0.0

    # Metrics that were emitted at this checkpoint
    emitted_metrics: dict[str, float] = field(default_factory=dict)

# Add new method to InstallationVerifier class
def verify_debug(
    self,
    categories: Optional[list[RequirementCategory]] = None,
    step_all: bool = False,
    on_checkpoint: Optional[Callable[[DebugCheckpoint], bool]] = None,
) -> VerificationResult:
    """
    Verify installation with debug checkpoints.

    Args:
        categories: Filter to specific categories (default: all)
        step_all: If True, checkpoint after each requirement; if False, after each category
        on_checkpoint: Callback called at each checkpoint. Return False to abort.

    Returns:
        VerificationResult with all check results
    """
    requirements = self._requirements
    if categories:
        requirements = [r for r in requirements if r.category in categories]

    # Group requirements by category
    by_category: dict[RequirementCategory, list[InstallationRequirement]] = {}
    for req in requirements:
        by_category.setdefault(req.category, []).append(req)

    all_results: list[RequirementResult] = []
    category_results_map: dict[RequirementCategory, list[RequirementResult]] = {}

    # Determine checkpoint counts
    if step_all:
        total_checkpoints = len(requirements)
    else:
        total_checkpoints = len(by_category)

    checkpoint_index = 0
    start_time = time.perf_counter()

    with tracer.start_as_current_span("contextcore.install.verify.debug") as parent_span:
        for category, cat_requirements in by_category.items():
            cat_results = []

            for req in cat_requirements:
                # Check the requirement
                result = self._check_requirement(req)
                all_results.append(result)
                cat_results.append(result)
                self._results_cache[req.id] = result

                # Emit telemetry for this requirement
                if self._emit_telemetry:
                    self._emit_requirement_telemetry(result, parent_span)

                # Per-requirement checkpoint
                if step_all and on_checkpoint:
                    checkpoint_index += 1

                    # Build emitted metrics dict
                    emitted = {
                        f'contextcore_install_requirement_status_ratio{{requirement_id="{req.id}"}}':
                            1.0 if result.passed else 0.0
                    }

                    checkpoint = DebugCheckpoint(
                        checkpoint_type="requirement",
                        checkpoint_index=checkpoint_index,
                        total_checkpoints=total_checkpoints,
                        requirement_result=result,
                        emitted_metrics=emitted
                    )

                    if not on_checkpoint(checkpoint):
                        # User requested abort
                        break

            category_results_map[category] = cat_results

            # Per-category checkpoint
            if not step_all and on_checkpoint:
                checkpoint_index += 1

                # Calculate category completeness
                passed = sum(1 for r in cat_results if r.passed)
                completeness = (passed / len(cat_results)) * 100 if cat_results else 0.0

                # Build emitted metrics dict
                emitted = {}
                for r in cat_results:
                    emitted[f'contextcore_install_requirement_status_ratio{{requirement_id="{r.requirement.id}"}}'] = \
                        1.0 if r.passed else 0.0
                emitted[f'contextcore_install_category_completeness_percent{{category="{category.value}"}}'] = completeness

                checkpoint = DebugCheckpoint(
                    checkpoint_type="category",
                    checkpoint_index=checkpoint_index,
                    total_checkpoints=total_checkpoints,
                    category=category,
                    category_results=cat_results,
                    category_completeness=completeness,
                    emitted_metrics=emitted
                )

                if not on_checkpoint(checkpoint):
                    # User requested abort
                    break

        # Calculate final results (same as regular verify)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Build category results
        cat_results_final = {}
        for cat, results in category_results_map.items():
            passed = sum(1 for r in results if r.passed)
            failed = sum(1 for r in results if r.status == RequirementStatus.FAILED)
            skipped = sum(1 for r in results if r.status == RequirementStatus.SKIPPED)
            errors = sum(1 for r in results if r.status == RequirementStatus.ERROR)
            cat_results_final[cat] = CategoryResult(
                category=cat,
                total=len(results),
                passed=passed,
                failed=failed,
                skipped=skipped,
                errors=errors
            )

        # Calculate totals
        total = len(all_results)
        passed = sum(1 for r in all_results if r.passed)
        failed = sum(1 for r in all_results if r.status == RequirementStatus.FAILED)
        critical_reqs = [r for r in all_results if r.requirement.critical]
        critical_met = sum(1 for r in critical_reqs if r.passed)
        critical_total = len(critical_reqs)
        completeness = (passed / total) * 100 if total > 0 else 0.0

        result = VerificationResult(
            results=all_results,
            categories=cat_results_final,
            total_requirements=total,
            passed_requirements=passed,
            failed_requirements=failed,
            critical_met=critical_met,
            critical_total=critical_total,
            completeness=completeness,
            duration_ms=duration_ms,
            verified_at=datetime.now(timezone.utc).isoformat(),
            is_complete=critical_met == critical_total
        )

        # Emit summary telemetry
        if self._emit_telemetry:
            self._emit_summary_telemetry(result)

        return result
```

---

### Step 4: Update CLI with Debug Flags

**File**: `src/contextcore/cli/install.py`

Add `--debug` and `--step-all` options to the verify command.

```python
# Add to imports
from contextcore.install.debug_display import (
    display_category_checkpoint,
    display_requirement_checkpoint,
    display_metrics_local,
    display_metric_comparison,
    prompt_continue,
    MetricComparison,
)
from contextcore.install.mimir_query import verify_metric_emitted

# Update install_verify command signature
@install.command("verify")
@click.option("--category", type=click.Choice([...]), help="...")
@click.option("--no-telemetry", is_flag=True, help="...")
@click.option("--endpoint", default="localhost:4317", help="...")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="...")
@click.option("--critical-only", is_flag=True, help="...")
@click.option("--debug", is_flag=True, help="Enable debug mode with step-by-step verification")
@click.option("--step-all", is_flag=True, help="In debug mode, pause after each requirement (not just category)")
def install_verify(category, no_telemetry, endpoint, format, critical_only, debug, step_all):
    """Verify ContextCore installation is complete."""

    # Existing OTel configuration code...
    if not no_telemetry:
        _configure_otel_providers(endpoint)

    from contextcore.install.verifier import InstallationVerifier, DebugCheckpoint
    from contextcore.install.requirements import INSTALLATION_REQUIREMENTS, RequirementCategory

    # Filter categories if specified
    categories = None
    if category:
        categories = [RequirementCategory(category)]

    verifier = InstallationVerifier(
        requirements=INSTALLATION_REQUIREMENTS,
        emit_telemetry=not no_telemetry
    )

    if debug:
        # Debug mode with checkpoints
        mimir_url = os.environ.get("MIMIR_URL", "http://localhost:9009")

        def on_checkpoint(checkpoint: DebugCheckpoint) -> bool:
            # 1. Force flush OTLP to ensure metrics are sent
            if not no_telemetry:
                _flush_otel_providers()
                # Small delay to allow Mimir to process
                import time
                time.sleep(0.5)

            # 2. Display checkpoint info
            if checkpoint.checkpoint_type == "category":
                display_category_checkpoint(
                    category_name=checkpoint.category.value,
                    category_index=checkpoint.checkpoint_index,
                    total_categories=checkpoint.total_checkpoints,
                    requirements_results=checkpoint.category_results,
                    category_completeness=checkpoint.category_completeness
                )
            else:
                display_requirement_checkpoint(
                    requirement_id=checkpoint.requirement_result.requirement.id,
                    requirement_index=checkpoint.checkpoint_index,
                    total_requirements=checkpoint.total_checkpoints,
                    result=checkpoint.requirement_result
                )

            # 3. Display local metrics
            display_metrics_local(checkpoint.emitted_metrics)

            # 4. Query Mimir and compare
            if not no_telemetry:
                comparisons = []
                for metric_key, local_value in checkpoint.emitted_metrics.items():
                    # Parse metric name and labels from key
                    # Format: metric_name{label="value",...}
                    if "{" in metric_key:
                        metric_name = metric_key.split("{")[0]
                        labels_str = metric_key.split("{")[1].rstrip("}")
                        labels = {}
                        for part in labels_str.split(","):
                            if "=" in part:
                                k, v = part.split("=", 1)
                                labels[k] = v.strip('"')
                    else:
                        metric_name = metric_key
                        labels = {}

                    success, mimir_value, error = verify_metric_emitted(
                        metric_name=metric_name,
                        expected_value=local_value,
                        labels=labels,
                        mimir_url=mimir_url
                    )

                    comparisons.append(MetricComparison(
                        metric_name=metric_name,
                        labels=labels,
                        local_value=local_value,
                        mimir_value=mimir_value,
                        match=success,
                        error=error
                    ))

                display_metric_comparison(comparisons)

            # 5. Prompt to continue
            return prompt_continue()

        result = verifier.verify_debug(
            categories=categories,
            step_all=step_all,
            on_checkpoint=on_checkpoint
        )
    else:
        # Normal verification
        result = verifier.verify(categories=categories)

    # Rest of existing output code...
```

---

## Files Summary

| File | Action | Lines Changed (Est.) |
|------|--------|---------------------|
| `src/contextcore/install/mimir_query.py` | **Create** | ~120 lines |
| `src/contextcore/install/debug_display.py` | **Create** | ~150 lines |
| `src/contextcore/install/verifier.py` | **Modify** | +150 lines |
| `src/contextcore/cli/install.py` | **Modify** | +80 lines |

---

## Usage Examples

### Default Debug Mode (Per-Category)

```bash
contextcore install verify --debug
```

Pauses 5 times (once per category: configuration, infrastructure, tooling, observability, documentation).

### Detailed Debug Mode (Per-Requirement)

```bash
contextcore install verify --debug --step-all
```

Pauses 28 times (once per requirement).

### Debug Without Telemetry Verification

```bash
contextcore install verify --debug --no-telemetry
```

Shows checkpoints but skips Mimir verification (useful when Mimir isn't running).

### Debug Specific Category

```bash
contextcore install verify --debug --category infrastructure
```

Only checks infrastructure requirements with debug output.

---

## Expected Output Format

```
════════════════════════════════════════════════════════════════════
 CATEGORY CHECKPOINT: INFRASTRUCTURE (3/5)
════════════════════════════════════════════════════════════════════

┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Status  ┃ Requirement ID          ┃ Result    ┃ Duration ┃ Error            ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ ✓       │ grafana_running         │ PASSED    │ 45ms     │                  │
│ ✓       │ tempo_running           │ PASSED    │ 52ms     │                  │
│ ✓       │ mimir_running           │ PASSED    │ 38ms     │                  │
│ ✗       │ loki_running            │ FAILED    │ 5002ms   │ Connection refused│
│ ✓       │ otlp_grpc_listening     │ PASSED    │ 12ms     │                  │
└─────────┴─────────────────────────┴───────────┴──────────┴──────────────────┘

Category Summary: Passed: 80.0%

╭──────────────────────────────────────────────────────────────────╮
│ METRICS EMITTED (Local)                                          │
╰──────────────────────────────────────────────────────────────────╯
  contextcore_install_requirement_status_ratio{requirement_id="grafana_running"} = 1.0
  contextcore_install_requirement_status_ratio{requirement_id="tempo_running"} = 1.0
  contextcore_install_requirement_status_ratio{requirement_id="mimir_running"} = 1.0
  contextcore_install_requirement_status_ratio{requirement_id="loki_running"} = 0.0
  contextcore_install_requirement_status_ratio{requirement_id="otlp_grpc_listening"} = 1.0
  contextcore_install_category_completeness_percent{category="infrastructure"} = 80.0

╭──────────────────────────────────────────────────────────────────╮
│ MIMIR VERIFICATION                                               │
╰──────────────────────────────────────────────────────────────────╯

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Metric                                           ┃ Local  ┃ Mimir  ┃ Match ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ contextcore_install_requirement_status_...       │ 1.0    │ 1.0    │ ✓     │
│ contextcore_install_requirement_status_...       │ 1.0    │ 1.0    │ ✓     │
│ contextcore_install_requirement_status_...       │ 1.0    │ 1.0    │ ✓     │
│ contextcore_install_requirement_status_...       │ 0.0    │ 0.0    │ ✓     │
│ contextcore_install_category_completeness_...    │ 80.0   │ 80.0   │ ✓     │
└──────────────────────────────────────────────────┴────────┴────────┴───────┘

All metrics verified! ✓

Press Enter to continue, or 'q' to quit...
```

---

## Verification Checklist

After implementation, verify:

- [ ] `contextcore install verify --debug` pauses 5 times (per category)
- [ ] `contextcore install verify --debug --step-all` pauses 28 times (per requirement)
- [ ] Local metrics displayed match what's expected
- [ ] Mimir queries return correct values
- [ ] Pressing Enter continues, pressing 'q' aborts
- [ ] `--no-telemetry` skips Mimir verification but still shows local values
- [ ] Existing `contextcore install verify` (without --debug) still works normally
- [ ] Exit code is correct (0 for complete, 1 for incomplete)

---

## Dependencies

All dependencies already exist in the project:
- `rich` - Used for tables and formatting
- `requests` - Used for HTTP calls
- `click` - CLI framework
- No new dependencies required
