"""
Dashboard provisioning module for ContextCore.

Provides Grafana dashboard provisioning for:
- Project Portfolio Overview
- Project Details
- Value Capabilities Dashboard

Example usage:
    from contextcore.dashboards import DashboardProvisioner

    provisioner = DashboardProvisioner(grafana_url="http://localhost:3000")
    provisioner.provision_all()
"""

from contextcore.dashboards.provisioner import (
    DashboardProvisioner,
    DashboardConfig,
)

__all__ = [
    "DashboardProvisioner",
    "DashboardConfig",
]
