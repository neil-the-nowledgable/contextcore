"""
Dashboard provisioner for Grafana.

Handles provisioning ContextCore dashboards to Grafana via API.
Supports auto-detection of Grafana URL and idempotent provisioning.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx


@dataclass
class DashboardConfig:
    """Configuration for a dashboard to provision."""

    name: str
    uid: str
    file_name: str
    description: str
    folder: str = "ContextCore"
    tags: list[str] = field(default_factory=lambda: ["contextcore"])


# Default dashboards to provision
DEFAULT_DASHBOARDS = [
    DashboardConfig(
        name="Project Portfolio Overview",
        uid="contextcore-portfolio",
        file_name="portfolio.json",
        description="Portfolio-level view of all projects with health indicators",
    ),
    DashboardConfig(
        name="Value Capabilities Dashboard",
        uid="contextcore-value-capabilities",
        file_name="value-capabilities.json",
        description="Developer dashboard for exploring value capabilities with multi-level filtering",
        tags=["contextcore", "value", "capabilities", "developer"],
    ),
]


class DashboardProvisioner:
    """
    Provision ContextCore dashboards to Grafana.

    Supports:
    - Auto-detection of Grafana URL from environment
    - API key or basic auth authentication
    - Idempotent provisioning (safe to run multiple times)
    - Folder organization
    - Dry-run mode for preview

    Example:
        provisioner = DashboardProvisioner(
            grafana_url="http://localhost:3000",
            api_key="your-api-key"
        )
        results = provisioner.provision_all()
        for name, success, message in results:
            print(f"{name}: {'OK' if success else 'FAILED'} - {message}")
    """

    def __init__(
        self,
        grafana_url: Optional[str] = None,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        folder_name: str = "ContextCore",
    ):
        """
        Initialize the provisioner.

        Args:
            grafana_url: Grafana base URL. Auto-detected from GRAFANA_URL env var.
            api_key: Grafana API key. Auto-detected from GRAFANA_API_KEY env var.
            username: Basic auth username. Auto-detected from GRAFANA_USERNAME env var.
            password: Basic auth password. Auto-detected from GRAFANA_PASSWORD env var.
            folder_name: Name of the folder to organize dashboards.
        """
        self.grafana_url = (
            grafana_url or os.environ.get("GRAFANA_URL", "http://localhost:3000")
        ).rstrip("/")
        self.api_key = api_key or os.environ.get("GRAFANA_API_KEY")
        self.username = username or os.environ.get("GRAFANA_USERNAME", "admin")
        self.password = password or os.environ.get("GRAFANA_PASSWORD", "admin")
        self.folder_name = folder_name
        self._folder_id: Optional[int] = None
        self._dashboards_dir = Path(__file__).parent

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for Grafana API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _get_auth(self) -> Optional[tuple[str, str]]:
        """Get basic auth credentials if no API key."""
        if self.api_key:
            return None
        return (self.username, self.password)

    def _ensure_folder(self, client: httpx.Client) -> int:
        """Ensure the ContextCore folder exists and return its ID."""
        if self._folder_id is not None:
            return self._folder_id

        # Check if folder exists
        response = client.get(
            f"{self.grafana_url}/api/folders",
            headers=self._get_headers(),
            auth=self._get_auth(),
        )
        response.raise_for_status()

        folders = response.json()
        for folder in folders:
            if folder.get("title") == self.folder_name:
                self._folder_id = folder["id"]
                return self._folder_id

        # Create folder
        response = client.post(
            f"{self.grafana_url}/api/folders",
            headers=self._get_headers(),
            auth=self._get_auth(),
            json={"title": self.folder_name},
        )
        response.raise_for_status()
        self._folder_id = response.json()["id"]
        return self._folder_id

    def _load_dashboard_json(self, file_name: str) -> dict:
        """Load dashboard JSON from file."""
        file_path = self._dashboards_dir / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"Dashboard file not found: {file_path}")

        with open(file_path) as f:
            return json.load(f)

    def provision_dashboard(
        self,
        config: DashboardConfig,
        dry_run: bool = False,
    ) -> tuple[str, bool, str]:
        """
        Provision a single dashboard to Grafana.

        Args:
            config: Dashboard configuration
            dry_run: If True, only validate without applying

        Returns:
            Tuple of (dashboard_name, success, message)
        """
        try:
            dashboard_json = self._load_dashboard_json(config.file_name)
        except FileNotFoundError as e:
            return (config.name, False, str(e))

        if dry_run:
            return (config.name, True, "Dry run - would provision")

        try:
            with httpx.Client(timeout=30.0) as client:
                folder_id = self._ensure_folder(client)

                # Prepare dashboard payload
                payload = {
                    "dashboard": dashboard_json,
                    "folderId": folder_id,
                    "overwrite": True,
                    "message": "Provisioned by ContextCore",
                }

                # Create/update dashboard
                response = client.post(
                    f"{self.grafana_url}/api/dashboards/db",
                    headers=self._get_headers(),
                    auth=self._get_auth(),
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    return (
                        config.name,
                        True,
                        f"Provisioned: {data.get('url', config.uid)}",
                    )
                else:
                    return (
                        config.name,
                        False,
                        f"HTTP {response.status_code}: {response.text}",
                    )

        except httpx.ConnectError:
            return (config.name, False, f"Cannot connect to Grafana at {self.grafana_url}")
        except Exception as e:
            return (config.name, False, str(e))

    def provision_all(
        self,
        dry_run: bool = False,
        dashboards: Optional[list[DashboardConfig]] = None,
    ) -> list[tuple[str, bool, str]]:
        """
        Provision all ContextCore dashboards.

        Args:
            dry_run: If True, only validate without applying
            dashboards: Optional list of dashboards to provision (defaults to all)

        Returns:
            List of (dashboard_name, success, message) tuples
        """
        if dashboards is None:
            dashboards = DEFAULT_DASHBOARDS

        results = []
        for config in dashboards:
            result = self.provision_dashboard(config, dry_run=dry_run)
            results.append(result)

        return results

    def list_provisioned(self) -> list[dict]:
        """
        List ContextCore dashboards currently in Grafana.

        Returns:
            List of dashboard info dicts with uid, title, url
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.grafana_url}/api/search",
                    headers=self._get_headers(),
                    auth=self._get_auth(),
                    params={"tag": "contextcore"},
                )
                response.raise_for_status()
                return response.json()
        except Exception:
            return []

    def delete_dashboard(self, uid: str) -> tuple[bool, str]:
        """
        Delete a dashboard by UID.

        Args:
            uid: Dashboard UID

        Returns:
            Tuple of (success, message)
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.delete(
                    f"{self.grafana_url}/api/dashboards/uid/{uid}",
                    headers=self._get_headers(),
                    auth=self._get_auth(),
                )

                if response.status_code == 200:
                    return (True, f"Deleted dashboard {uid}")
                elif response.status_code == 404:
                    return (True, f"Dashboard {uid} not found (already deleted)")
                else:
                    return (False, f"HTTP {response.status_code}: {response.text}")

        except httpx.ConnectError:
            return (False, f"Cannot connect to Grafana at {self.grafana_url}")
        except Exception as e:
            return (False, str(e))

    def delete_all(self) -> list[tuple[str, bool, str]]:
        """
        Delete all ContextCore dashboards from Grafana.

        Returns:
            List of (uid, success, message) tuples
        """
        results = []
        for config in DEFAULT_DASHBOARDS:
            success, message = self.delete_dashboard(config.uid)
            results.append((config.uid, success, message))
        return results
