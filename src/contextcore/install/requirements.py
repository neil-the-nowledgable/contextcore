"""
Installation requirements for ContextCore.

Defines what constitutes a complete ContextCore installation, organized by
category. Each requirement has a check function that returns True if met.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

import httpx


class RequirementCategory(str, Enum):
    """Categories of installation requirements."""

    CONFIGURATION = "configuration"  # Config files present
    INFRASTRUCTURE = "infrastructure"  # Docker, services running
    TOOLING = "tooling"  # CLI, make targets available
    OBSERVABILITY = "observability"  # Grafana datasources, dashboards
    DOCUMENTATION = "documentation"  # Runbooks, guides


class RequirementStatus(str, Enum):
    """Status of a requirement check."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class InstallationRequirement:
    """A single installation requirement."""

    id: str
    name: str
    description: str
    category: RequirementCategory
    check: Callable[[], bool]
    critical: bool = True  # If True, installation is incomplete without it
    depends_on: list[str] = field(default_factory=list)

    # Telemetry attributes
    metric_name: str = ""  # e.g., "contextcore.install.config.docker_compose"
    span_name: str = ""  # e.g., "install.verify.docker_compose"

    def __post_init__(self):
        if not self.metric_name:
            self.metric_name = f"contextcore.install.{self.category.value}.{self.id}"
        if not self.span_name:
            self.span_name = f"install.verify.{self.id}"


def _find_project_root() -> Optional[Path]:
    """Find the ContextCore project root."""
    # Try current directory first
    cwd = Path.cwd()
    if (cwd / "docker-compose.yaml").exists():
        return cwd

    # Try parent directories
    for parent in cwd.parents:
        if (parent / "docker-compose.yaml").exists():
            return parent
        if (parent / "pyproject.toml").exists():
            with open(parent / "pyproject.toml") as f:
                if "contextcore" in f.read():
                    return parent

    return None


# =============================================================================
# Check Functions
# =============================================================================


def check_docker_compose_exists() -> bool:
    """Check if docker-compose.yaml exists."""
    root = _find_project_root()
    return root is not None and (root / "docker-compose.yaml").exists()


def check_makefile_exists() -> bool:
    """Check if Makefile exists."""
    root = _find_project_root()
    return root is not None and (root / "Makefile").exists()


def check_tempo_config() -> bool:
    """Check if Tempo configuration exists."""
    root = _find_project_root()
    return root is not None and (root / "tempo" / "tempo.yaml").exists()


def check_mimir_config() -> bool:
    """Check if Mimir configuration exists."""
    root = _find_project_root()
    return root is not None and (root / "mimir" / "mimir.yaml").exists()


def check_loki_config() -> bool:
    """Check if Loki configuration exists."""
    root = _find_project_root()
    return root is not None and (root / "loki" / "loki.yaml").exists()


def check_grafana_datasources() -> bool:
    """Check if Grafana datasources provisioning exists."""
    root = _find_project_root()
    if root is None:
        return False
    path = root / "grafana" / "provisioning" / "datasources" / "datasources.yaml"
    return path.exists()


def check_grafana_dashboards_provisioning() -> bool:
    """Check if Grafana dashboards provisioning exists."""
    root = _find_project_root()
    if root is None:
        return False
    path = root / "grafana" / "provisioning" / "dashboards" / "dashboards.yaml"
    return path.exists()


def check_ops_module() -> bool:
    """Check if ops module is installed."""
    try:
        from contextcore import ops

        return hasattr(ops, "doctor") and hasattr(ops, "health_check")
    except ImportError:
        return False


def check_install_module() -> bool:
    """Check if install module is installed."""
    try:
        from contextcore import install

        return hasattr(install, "verify_installation")
    except ImportError:
        return False


def check_cli_installed() -> bool:
    """Check if contextcore CLI is available."""
    return shutil.which("contextcore") is not None


def check_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_make_available() -> bool:
    """Check if make is available."""
    return shutil.which("make") is not None


def check_grafana_running() -> bool:
    """Check if Grafana is running and healthy."""
    try:
        response = httpx.get("http://localhost:3000/api/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def check_tempo_running() -> bool:
    """Check if Tempo is running and healthy."""
    try:
        response = httpx.get("http://localhost:3200/ready", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def check_mimir_running() -> bool:
    """Check if Mimir is running and healthy."""
    try:
        response = httpx.get("http://localhost:9009/ready", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def check_loki_running() -> bool:
    """Check if Loki is running and healthy."""
    try:
        response = httpx.get("http://localhost:3100/ready", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def check_otlp_grpc_listening() -> bool:
    """Check if OTLP gRPC endpoint is listening."""
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 4317))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_otlp_http_listening() -> bool:
    """Check if OTLP HTTP endpoint is listening."""
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 4318))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_grafana_has_tempo_datasource() -> bool:
    """Check if Grafana has Tempo datasource configured."""
    try:
        response = httpx.get(
            "http://localhost:3000/api/datasources",
            auth=("admin", "admin"),
            timeout=5,
        )
        if response.status_code == 200:
            datasources = response.json()
            return any(ds.get("type") == "tempo" for ds in datasources)
        return False
    except Exception:
        return False


def check_grafana_has_mimir_datasource() -> bool:
    """Check if Grafana has Mimir/Prometheus datasource configured."""
    try:
        response = httpx.get(
            "http://localhost:3000/api/datasources",
            auth=("admin", "admin"),
            timeout=5,
        )
        if response.status_code == 200:
            datasources = response.json()
            return any(ds.get("type") == "prometheus" for ds in datasources)
        return False
    except Exception:
        return False


def check_grafana_has_loki_datasource() -> bool:
    """Check if Grafana has Loki datasource configured."""
    try:
        response = httpx.get(
            "http://localhost:3000/api/datasources",
            auth=("admin", "admin"),
            timeout=5,
        )
        if response.status_code == 200:
            datasources = response.json()
            return any(ds.get("type") == "loki" for ds in datasources)
        return False
    except Exception:
        return False


def check_grafana_has_dashboards() -> bool:
    """Check if Grafana has ContextCore dashboards."""
    try:
        response = httpx.get(
            "http://localhost:3000/api/search?type=dash-db",
            auth=("admin", "admin"),
            timeout=5,
        )
        if response.status_code == 200:
            dashboards = response.json()
            # Check for at least one dashboard
            return len(dashboards) > 0
        return False
    except Exception:
        return False


def check_operational_resilience_doc() -> bool:
    """Check if operational resilience documentation exists."""
    root = _find_project_root()
    if root is None:
        return False
    return (root / "docs" / "OPERATIONAL_RESILIENCE.md").exists()


def check_operational_runbook() -> bool:
    """Check if operational runbook exists."""
    root = _find_project_root()
    if root is None:
        return False
    return (root / "docs" / "OPERATIONAL_RUNBOOK.md").exists()


def check_data_directories() -> bool:
    """Check if data directories exist for persistence."""
    root = _find_project_root()
    if root is None:
        return False
    data_dir = root / "data"
    if not data_dir.exists():
        return False
    # Check for at least some subdirectories
    subdirs = ["grafana", "tempo", "mimir", "loki"]
    return any((data_dir / subdir).exists() for subdir in subdirs)


# =============================================================================
# Installation Requirements Registry
# =============================================================================

INSTALLATION_REQUIREMENTS: list[InstallationRequirement] = [
    # Configuration
    InstallationRequirement(
        id="docker_compose",
        name="Docker Compose Configuration",
        description="docker-compose.yaml exists with service definitions",
        category=RequirementCategory.CONFIGURATION,
        check=check_docker_compose_exists,
        critical=True,
    ),
    InstallationRequirement(
        id="makefile",
        name="Makefile",
        description="Makefile with operational targets (doctor, up, health, etc.)",
        category=RequirementCategory.CONFIGURATION,
        check=check_makefile_exists,
        critical=True,
    ),
    InstallationRequirement(
        id="tempo_config",
        name="Tempo Configuration",
        description="tempo/tempo.yaml with OTLP receivers and storage",
        category=RequirementCategory.CONFIGURATION,
        check=check_tempo_config,
        critical=True,
    ),
    InstallationRequirement(
        id="mimir_config",
        name="Mimir Configuration",
        description="mimir/mimir.yaml with metrics storage",
        category=RequirementCategory.CONFIGURATION,
        check=check_mimir_config,
        critical=True,
    ),
    InstallationRequirement(
        id="loki_config",
        name="Loki Configuration",
        description="loki/loki.yaml with log storage",
        category=RequirementCategory.CONFIGURATION,
        check=check_loki_config,
        critical=True,
    ),
    InstallationRequirement(
        id="grafana_datasources_config",
        name="Grafana Datasources Provisioning",
        description="Grafana datasources auto-provisioning configuration",
        category=RequirementCategory.CONFIGURATION,
        check=check_grafana_datasources,
        critical=True,
    ),
    InstallationRequirement(
        id="grafana_dashboards_config",
        name="Grafana Dashboards Provisioning",
        description="Grafana dashboards auto-provisioning configuration",
        category=RequirementCategory.CONFIGURATION,
        check=check_grafana_dashboards_provisioning,
        critical=False,
    ),
    # Tooling
    InstallationRequirement(
        id="cli_installed",
        name="ContextCore CLI",
        description="contextcore command available in PATH",
        category=RequirementCategory.TOOLING,
        check=check_cli_installed,
        critical=True,
    ),
    InstallationRequirement(
        id="ops_module",
        name="Operations Module",
        description="contextcore.ops module with doctor, health, backup",
        category=RequirementCategory.TOOLING,
        check=check_ops_module,
        critical=True,
    ),
    InstallationRequirement(
        id="install_module",
        name="Installation Module",
        description="contextcore.install module with verification",
        category=RequirementCategory.TOOLING,
        check=check_install_module,
        critical=False,
    ),
    InstallationRequirement(
        id="docker_available",
        name="Docker Available",
        description="Docker daemon is running and accessible",
        category=RequirementCategory.TOOLING,
        check=check_docker_available,
        critical=True,
    ),
    InstallationRequirement(
        id="make_available",
        name="Make Available",
        description="make command available for operational targets",
        category=RequirementCategory.TOOLING,
        check=check_make_available,
        critical=False,
    ),
    # Infrastructure
    InstallationRequirement(
        id="grafana_running",
        name="Grafana Running",
        description="Grafana service healthy at localhost:3000",
        category=RequirementCategory.INFRASTRUCTURE,
        check=check_grafana_running,
        critical=True,
        depends_on=["docker_compose", "docker_available"],
    ),
    InstallationRequirement(
        id="tempo_running",
        name="Tempo Running",
        description="Tempo service healthy at localhost:3200",
        category=RequirementCategory.INFRASTRUCTURE,
        check=check_tempo_running,
        critical=True,
        depends_on=["docker_compose", "docker_available", "tempo_config"],
    ),
    InstallationRequirement(
        id="mimir_running",
        name="Mimir Running",
        description="Mimir service healthy at localhost:9009",
        category=RequirementCategory.INFRASTRUCTURE,
        check=check_mimir_running,
        critical=True,
        depends_on=["docker_compose", "docker_available", "mimir_config"],
    ),
    InstallationRequirement(
        id="loki_running",
        name="Loki Running",
        description="Loki service healthy at localhost:3100",
        category=RequirementCategory.INFRASTRUCTURE,
        check=check_loki_running,
        critical=True,
        depends_on=["docker_compose", "docker_available", "loki_config"],
    ),
    InstallationRequirement(
        id="otlp_grpc",
        name="OTLP gRPC Endpoint",
        description="OTLP gRPC receiver listening at localhost:4317",
        category=RequirementCategory.INFRASTRUCTURE,
        check=check_otlp_grpc_listening,
        critical=True,
        depends_on=["tempo_running"],
    ),
    InstallationRequirement(
        id="otlp_http",
        name="OTLP HTTP Endpoint",
        description="OTLP HTTP receiver listening at localhost:4318",
        category=RequirementCategory.INFRASTRUCTURE,
        check=check_otlp_http_listening,
        critical=True,
        depends_on=["tempo_running"],
    ),
    InstallationRequirement(
        id="data_persistence",
        name="Data Persistence",
        description="Data directories exist for persistent storage",
        category=RequirementCategory.INFRASTRUCTURE,
        check=check_data_directories,
        critical=True,
        depends_on=["docker_compose"],
    ),
    # Observability
    InstallationRequirement(
        id="grafana_tempo_datasource",
        name="Tempo Datasource",
        description="Grafana has Tempo datasource for traces",
        category=RequirementCategory.OBSERVABILITY,
        check=check_grafana_has_tempo_datasource,
        critical=True,
        depends_on=["grafana_running"],
    ),
    InstallationRequirement(
        id="grafana_mimir_datasource",
        name="Mimir Datasource",
        description="Grafana has Mimir/Prometheus datasource for metrics",
        category=RequirementCategory.OBSERVABILITY,
        check=check_grafana_has_mimir_datasource,
        critical=True,
        depends_on=["grafana_running"],
    ),
    InstallationRequirement(
        id="grafana_loki_datasource",
        name="Loki Datasource",
        description="Grafana has Loki datasource for logs",
        category=RequirementCategory.OBSERVABILITY,
        check=check_grafana_has_loki_datasource,
        critical=True,
        depends_on=["grafana_running"],
    ),
    InstallationRequirement(
        id="grafana_dashboards",
        name="Dashboards Provisioned",
        description="ContextCore dashboards available in Grafana",
        category=RequirementCategory.OBSERVABILITY,
        check=check_grafana_has_dashboards,
        critical=False,
        depends_on=["grafana_running"],
    ),
    # Documentation
    InstallationRequirement(
        id="operational_resilience_doc",
        name="Operational Resilience Guide",
        description="docs/OPERATIONAL_RESILIENCE.md with architecture",
        category=RequirementCategory.DOCUMENTATION,
        check=check_operational_resilience_doc,
        critical=False,
    ),
    InstallationRequirement(
        id="operational_runbook",
        name="Operational Runbook",
        description="docs/OPERATIONAL_RUNBOOK.md with quick reference",
        category=RequirementCategory.DOCUMENTATION,
        check=check_operational_runbook,
        critical=False,
    ),
]


def get_requirements_by_category(
    category: RequirementCategory,
) -> list[InstallationRequirement]:
    """Get all requirements for a specific category."""
    return [r for r in INSTALLATION_REQUIREMENTS if r.category == category]


def get_critical_requirements() -> list[InstallationRequirement]:
    """Get all critical requirements."""
    return [r for r in INSTALLATION_REQUIREMENTS if r.critical]


def get_requirement_by_id(req_id: str) -> Optional[InstallationRequirement]:
    """Get a requirement by its ID."""
    for req in INSTALLATION_REQUIREMENTS:
        if req.id == req_id:
            return req
    return None
