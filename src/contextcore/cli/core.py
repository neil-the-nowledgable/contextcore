"""ContextCore CLI - Core commands (create, annotate, generate, runbook, controller)."""

import json
import os
import sys
from typing import Optional

import click
import yaml

from ._generators import generate_service_monitor, generate_prometheus_rule, generate_dashboard


def _get_project_context_spec(project: str, namespace: str = "default") -> Optional[dict]:
    """Fetch ProjectContext spec from Kubernetes cluster."""
    import subprocess

    if "/" in project:
        namespace, name = project.split("/", 1)
    else:
        name = project

    cmd = ["kubectl", "get", "projectcontext", name, "-n", namespace, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None

    pc = json.loads(result.stdout)
    return pc.get("spec", {})


@click.command()
@click.option("--name", "-n", required=True, help="ProjectContext name")
@click.option("--namespace", default="default", help="K8s namespace")
@click.option("--project", "-p", required=True, help="Project identifier")
@click.option("--epic", help="Epic identifier")
@click.option("--task", multiple=True, help="Task identifiers (can specify multiple)")
@click.option("--criticality", type=click.Choice(["critical", "high", "medium", "low"]), help="Business criticality")
@click.option("--value", type=click.Choice(["revenue-primary", "revenue-secondary", "cost-reduction", "compliance", "enabler"]), help="Business value")
@click.option("--owner", help="Owning team")
@click.option("--design-doc", help="Design document URL")
@click.option("--adr", help="ADR identifier or URL")
@click.option("--target", multiple=True, help="Target resources (kind/name)")
@click.option("--output", "-o", type=click.Choice(["yaml", "json"]), default="yaml")
@click.option("--apply", is_flag=True, help="Apply to cluster (requires kubectl)")
def create(name: str, namespace: str, project: str, epic: Optional[str], task: tuple, criticality: Optional[str],
           value: Optional[str], owner: Optional[str], design_doc: Optional[str], adr: Optional[str],
           target: tuple, output: str, apply: bool):
    """Create a new ProjectContext resource."""
    spec = {"project": {"id": project}, "targets": []}

    if epic:
        spec["project"]["epic"] = epic
    if task:
        spec["project"]["tasks"] = list(task)

    if criticality or value or owner:
        spec["business"] = {}
        if criticality:
            spec["business"]["criticality"] = criticality
        if value:
            spec["business"]["value"] = value
        if owner:
            spec["business"]["owner"] = owner

    if design_doc or adr:
        spec["design"] = {}
        if design_doc:
            spec["design"]["doc"] = design_doc
        if adr:
            spec["design"]["adr"] = adr

    if target:
        for t in target:
            if "/" in t:
                kind, tname = t.split("/", 1)
                spec["targets"].append({"kind": kind, "name": tname})
            else:
                click.echo(f"Invalid target format: {t}. Use kind/name", err=True)
                sys.exit(1)
    else:
        spec["targets"].append({"kind": "Deployment", "name": name})

    resource = {
        "apiVersion": "contextcore.io/v1",
        "kind": "ProjectContext",
        "metadata": {"name": name, "namespace": namespace},
        "spec": spec,
    }

    if output == "yaml":
        click.echo(yaml.dump(resource, default_flow_style=False))
    else:
        click.echo(json.dumps(resource, indent=2))

    if apply:
        import subprocess
        yaml_content = yaml.dump(resource)
        result = subprocess.run(["kubectl", "apply", "-f", "-"], input=yaml_content, capture_output=True, text=True)
        if result.returncode != 0:
            click.echo(f"Error applying: {result.stderr}", err=True)
            sys.exit(1)
        click.echo(result.stdout)


@click.command()
@click.argument("resource")
@click.option("--context", "-c", required=True, help="ProjectContext name")
@click.option("--namespace", "-n", default="default", help="Namespace")
def annotate(resource: str, context: str, namespace: str):
    """Annotate a K8s resource with ProjectContext reference."""
    import subprocess

    if "/" not in resource:
        click.echo("Resource should be in format kind/name", err=True)
        sys.exit(1)

    annotation = f"contextcore.io/projectcontext={context}"
    cmd = ["kubectl", "annotate", resource, annotation, "-n", namespace, "--overwrite"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        click.echo(f"Error: {result.stderr}", err=True)
        sys.exit(1)

    click.echo(f"Annotated {resource} with {annotation}")


@click.command()
@click.option("--context", "-c", required=True, help="ProjectContext (namespace/name)")
@click.option("--output", "-o", default="./generated", help="Output directory")
@click.option("--service-monitor", is_flag=True, help="Generate ServiceMonitor")
@click.option("--prometheus-rule", is_flag=True, help="Generate PrometheusRule")
@click.option("--dashboard", is_flag=True, help="Generate Grafana dashboard")
@click.option("--all", "generate_all", is_flag=True, help="Generate all artifacts")
def generate(context: str, output: str, service_monitor: bool, prometheus_rule: bool, dashboard: bool, generate_all: bool):
    """Generate observability artifacts from ProjectContext."""
    import subprocess

    if "/" in context:
        namespace, name = context.split("/", 1)
    else:
        namespace = "default"
        name = context

    cmd = ["kubectl", "get", "projectcontext", name, "-n", namespace, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        click.echo(f"Error getting ProjectContext: {result.stderr}", err=True)
        sys.exit(1)

    pc = json.loads(result.stdout)
    spec = pc.get("spec", {})

    os.makedirs(output, exist_ok=True)

    if generate_all:
        service_monitor = prometheus_rule = dashboard = True

    generated = []

    if service_monitor:
        sm = generate_service_monitor(name, namespace, spec)
        path = os.path.join(output, f"{name}-servicemonitor.yaml")
        with open(path, "w") as f:
            yaml.dump(sm, f)
        generated.append(path)

    if prometheus_rule:
        pr = generate_prometheus_rule(name, namespace, spec)
        path = os.path.join(output, f"{name}-prometheusrule.yaml")
        with open(path, "w") as f:
            yaml.dump(pr, f)
        generated.append(path)

    if dashboard:
        db = generate_dashboard(name, namespace, spec)
        path = os.path.join(output, f"{name}-dashboard.json")
        with open(path, "w") as f:
            json.dump(db, f, indent=2)
        generated.append(path)

    if generated:
        click.echo(f"Generated {len(generated)} artifacts in {output}/")
        for path in generated:
            click.echo(f"  - {path}")
    else:
        click.echo("No artifacts generated. Use --all or specific flags.")


@click.command()
@click.option("--project", "-p", required=True, help="ProjectContext name (or namespace/name)")
@click.option("--namespace", "-n", default="default", help="Kubernetes namespace")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "output_format", default="markdown", type=click.Choice(["markdown"]))
@click.option("--from-file", type=click.Path(exists=True), help="Read spec from local YAML file")
def runbook(project: str, namespace: str, output: Optional[str], output_format: str, from_file: Optional[str]):
    """Generate operational runbook from ProjectContext."""
    from contextcore.generators.runbook import generate_runbook

    if from_file:
        with open(from_file) as f:
            data = yaml.safe_load(f)
        spec = data.get("spec", data)
        project_info = spec.get("project", {})
        if isinstance(project_info, dict):
            project_id = project_info.get("id", project)
        else:
            project_id = project_info or project
    else:
        spec = _get_project_context_spec(project, namespace)
        if spec is None:
            click.echo(f"Error: ProjectContext '{project}' not found in namespace '{namespace}'", err=True)
            sys.exit(1)
        project_info = spec.get("project", {})
        if isinstance(project_info, dict):
            project_id = project_info.get("id", project)
        else:
            project_id = project_info or project

    runbook_content = generate_runbook(project_id, spec, output_format)

    if output:
        with open(output, "w") as f:
            f.write(runbook_content)
        click.echo(f"Runbook written to {output}")
    else:
        click.echo(runbook_content)


@click.command()
@click.option("--kubeconfig", envvar="KUBECONFIG", help="Path to kubeconfig")
@click.option("--namespace", default="", help="Namespace to watch (empty for all)")
def controller(kubeconfig: Optional[str], namespace: str):
    """Run the ContextCore controller locally."""
    import subprocess

    click.echo("Starting ContextCore controller...")
    click.echo(f"  kubeconfig: {kubeconfig or 'in-cluster'}")
    click.echo(f"  namespace: {namespace or 'all'}")

    cmd = ["kopf", "run", "-m", "contextcore.operator", "--verbose"]
    if namespace:
        cmd.extend(["--namespace", namespace])

    click.echo(f"  Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        click.echo("Error: kopf not found. Install with: pip install kopf", err=True)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        click.echo(f"Controller exited with error: {e.returncode}", err=True)
        sys.exit(e.returncode)
