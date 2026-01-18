"""ContextCore CLI - Installation verification commands."""

import json
import sys
from typing import Optional

import click


@click.group()
def install():
    """Installation verification and status."""
    pass


@install.command("verify")
@click.option(
    "--category",
    "-c",
    multiple=True,
    type=click.Choice(
        ["configuration", "infrastructure", "tooling", "observability", "documentation"]
    ),
    help="Check specific categories only",
)
@click.option(
    "--no-telemetry",
    is_flag=True,
    help="Skip emitting telemetry",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.option(
    "--critical-only",
    is_flag=True,
    help="Only show critical requirements",
)
def install_verify(category, no_telemetry, output_format, critical_only):
    """Verify ContextCore installation completeness.

    Checks all installation requirements and emits telemetry about the
    installation state. This enables ContextCore to track its own setup
    as observable data.

    Examples:

        # Full verification
        contextcore install verify

        # Check infrastructure only
        contextcore install verify --category infrastructure

        # JSON output for automation
        contextcore install verify --format json
    """
    from contextcore.install import (
        RequirementCategory,
        verify_installation,
    )

    # Map category strings to enums
    categories = None
    if category:
        categories = [RequirementCategory(c) for c in category]

    # Run verification
    result = verify_installation(
        categories=categories,
        emit_telemetry=not no_telemetry,
    )

    if output_format == "json":
        click.echo(json.dumps(result.to_dict(), indent=2))
        return

    # Table output
    click.echo()
    click.echo(click.style("=== ContextCore Installation Verification ===", fg="cyan"))
    click.echo()

    # Summary
    status_color = "green" if result.is_complete else "yellow"
    click.echo(
        f"Status: {click.style('COMPLETE' if result.is_complete else 'INCOMPLETE', fg=status_color, bold=True)}"
    )
    click.echo(f"Completeness: {result.completeness:.1f}%")
    click.echo(
        f"Critical: {result.critical_met}/{result.critical_total} "
        f"({result.critical_met / result.critical_total * 100:.0f}%)"
        if result.critical_total > 0
        else "Critical: N/A"
    )
    click.echo(f"Total: {result.passed_requirements}/{result.total_requirements}")
    click.echo(f"Duration: {result.duration_ms:.1f}ms")
    click.echo()

    # Category breakdown
    click.echo(click.style("By Category:", bold=True))
    for cat, cat_result in result.categories.items():
        cat_color = "green" if cat_result.completeness == 100 else "yellow"
        click.echo(
            f"  {cat.value:15} {click.style(f'{cat_result.completeness:5.1f}%', fg=cat_color)} "
            f"({cat_result.passed}/{cat_result.total})"
        )
    click.echo()

    # Requirements details
    click.echo(click.style("Requirements:", bold=True))

    for req_result in result.results:
        req = req_result.requirement

        # Skip non-critical if requested
        if critical_only and not req.critical:
            continue

        # Status indicator
        if req_result.status.value == "passed":
            indicator = click.style("[PASS]", fg="green")
        elif req_result.status.value == "skipped":
            indicator = click.style("[SKIP]", fg="yellow")
        elif req_result.status.value == "error":
            indicator = click.style("[ERR]", fg="red")
        else:
            indicator = click.style("[FAIL]", fg="red")

        # Critical badge
        critical_badge = click.style(" [CRITICAL]", fg="red") if req.critical else ""

        click.echo(f"  {indicator} {req.name}{critical_badge}")

        # Show error details
        if req_result.error:
            click.echo(f"      {click.style(req_result.error, fg='red')}")

    click.echo()

    # Exit code
    if not result.is_complete:
        click.echo(
            click.style(
                f"Installation incomplete: {result.critical_total - result.critical_met} critical requirements missing",
                fg="yellow",
            )
        )
        sys.exit(1)
    else:
        click.echo(click.style("Installation complete!", fg="green"))


@install.command("status")
def install_status():
    """Quick installation status check (no telemetry).

    Returns a simple status summary without emitting any telemetry.
    Useful for quick checks or CI/CD pipelines.
    """
    from contextcore.install import verify_installation

    result = verify_installation(emit_telemetry=False)

    if result.is_complete:
        click.echo(click.style("Complete", fg="green"))
        click.echo(f"   {result.passed_requirements}/{result.total_requirements} requirements met")
    else:
        click.echo(click.style("Incomplete", fg="red"))
        click.echo(f"   {result.critical_met}/{result.critical_total} critical requirements met")
        click.echo(f"   {result.passed_requirements}/{result.total_requirements} total requirements met")

    sys.exit(0 if result.is_complete else 1)


@install.command("list-requirements")
@click.option(
    "--category",
    "-c",
    type=click.Choice(
        ["configuration", "infrastructure", "tooling", "observability", "documentation"]
    ),
    help="Filter by category",
)
@click.option(
    "--critical-only",
    is_flag=True,
    help="Only show critical requirements",
)
def install_list_requirements(category, critical_only):
    """List all installation requirements.

    Shows the complete list of requirements that ContextCore checks
    during installation verification.
    """
    from contextcore.install import (
        INSTALLATION_REQUIREMENTS,
        RequirementCategory,
        get_requirements_by_category,
    )

    if category:
        requirements = get_requirements_by_category(RequirementCategory(category))
    else:
        requirements = INSTALLATION_REQUIREMENTS

    if critical_only:
        requirements = [r for r in requirements if r.critical]

    click.echo()
    click.echo(click.style("=== Installation Requirements ===", fg="cyan"))
    click.echo()

    current_category = None
    for req in requirements:
        # Category header
        if req.category != current_category:
            current_category = req.category
            click.echo(click.style(f"\n{current_category.value.upper()}", bold=True))

        # Requirement details
        critical_badge = click.style(" [CRITICAL]", fg="red") if req.critical else ""
        click.echo(f"  {req.id}{critical_badge}")
        click.echo(f"    {req.description}")

        if req.depends_on:
            deps = ", ".join(req.depends_on)
            click.echo(f"    Depends on: {deps}")

    click.echo()
    click.echo(f"Total: {len(requirements)} requirements")
