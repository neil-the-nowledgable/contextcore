"""ContextCore CLI - Dashboard provisioning commands."""

from typing import Optional

import click


@click.group()
def dashboards():
    """Provision and manage Grafana dashboards."""
    pass


@dashboards.command("provision")
@click.option("--grafana-url", envvar="GRAFANA_URL", default="http://localhost:3000", help="Grafana base URL")
@click.option("--api-key", envvar="GRAFANA_API_KEY", help="Grafana API key")
@click.option("--username", envvar="GRAFANA_USERNAME", default="admin", help="Grafana username")
@click.option("--password", envvar="GRAFANA_PASSWORD", default="admin", help="Grafana password")
@click.option("--dry-run", is_flag=True, help="Preview without applying")
def dashboards_provision(grafana_url: str, api_key: Optional[str], username: str, password: str, dry_run: bool):
    """Provision ContextCore dashboards to Grafana."""
    from contextcore.dashboards import DashboardProvisioner

    click.echo(click.style("ContextCore Dashboard Provisioning", fg="cyan", bold=True))
    click.echo()

    if dry_run:
        click.echo(click.style("DRY RUN MODE - No changes will be made", fg="yellow"))
        click.echo()

    click.echo(f"Grafana URL: {grafana_url}")
    click.echo(f"Auth: {'API Key' if api_key else 'Basic Auth'}")
    click.echo()

    provisioner = DashboardProvisioner(
        grafana_url=grafana_url,
        api_key=api_key,
        username=username,
        password=password,
    )

    results = provisioner.provision_all(dry_run=dry_run)

    click.echo(click.style("Results:", bold=True))
    success_count = 0
    for name, success, message in results:
        if success:
            click.echo(f"  {click.style('[OK]', fg='green')} {name}: {message}")
            success_count += 1
        else:
            click.echo(f"  {click.style('[ERR]', fg='red')} {name}: {message}")

    click.echo()
    click.echo(f"Provisioned {success_count}/{len(results)} dashboards")


@dashboards.command("list")
@click.option("--grafana-url", envvar="GRAFANA_URL", default="http://localhost:3000", help="Grafana base URL")
@click.option("--api-key", envvar="GRAFANA_API_KEY", help="Grafana API key")
@click.option("--username", envvar="GRAFANA_USERNAME", default="admin", help="Grafana username")
@click.option("--password", envvar="GRAFANA_PASSWORD", default="admin", help="Grafana password")
def dashboards_list(grafana_url: str, api_key: Optional[str], username: str, password: str):
    """List ContextCore dashboards in Grafana."""
    from contextcore.dashboards import DashboardProvisioner

    provisioner = DashboardProvisioner(
        grafana_url=grafana_url,
        api_key=api_key,
        username=username,
        password=password,
    )

    dashboards_found = provisioner.list_provisioned()

    if not dashboards_found:
        click.echo("No ContextCore dashboards found in Grafana")
        click.echo()
        click.echo("Run 'contextcore dashboards provision' to create them")
        return

    click.echo(click.style("ContextCore Dashboards:", fg="cyan", bold=True))
    click.echo()

    for db in dashboards_found:
        click.echo(f"  {click.style(db.get('title', 'Unknown'), bold=True)}")
        click.echo(f"    UID: {db.get('uid', 'N/A')}")
        click.echo(f"    URL: {grafana_url}{db.get('url', '')}")
        click.echo()


@dashboards.command("delete")
@click.option("--grafana-url", envvar="GRAFANA_URL", default="http://localhost:3000", help="Grafana base URL")
@click.option("--api-key", envvar="GRAFANA_API_KEY", help="Grafana API key")
@click.option("--username", envvar="GRAFANA_USERNAME", default="admin", help="Grafana username")
@click.option("--password", envvar="GRAFANA_PASSWORD", default="admin", help="Grafana password")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def dashboards_delete(grafana_url: str, api_key: Optional[str], username: str, password: str, yes: bool):
    """Delete ContextCore dashboards from Grafana."""
    from contextcore.dashboards import DashboardProvisioner

    if not yes:
        if not click.confirm("Delete all ContextCore dashboards?"):
            click.echo("Cancelled")
            return

    provisioner = DashboardProvisioner(
        grafana_url=grafana_url,
        api_key=api_key,
        username=username,
        password=password,
    )

    results = provisioner.delete_all()

    click.echo(click.style("Deletion Results:", bold=True))
    for uid, success, message in results:
        if success:
            click.echo(f"  {click.style('[OK]', fg='green')} {uid}: {message}")
        else:
            click.echo(f"  {click.style('[ERR]', fg='red')} {uid}: {message}")
