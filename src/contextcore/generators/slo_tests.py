"""
SLO-Driven Test Generation module for ContextCore.

This module generates load tests (k6) and chaos tests (chaos-mesh) directly from
ProjectContext requirements, eliminating manual test specification.

Prime Contractor Pattern: Spec by Claude, drafts by GPT-4o-mini, integration by Claude.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
import re

__all__ = [
    'TestType', 'GeneratedTest', 'SLOTestGenerator',
    'parse_duration', 'parse_throughput', 'write_tests'
]


class TestType(Enum):
    """Enumeration of supported test types."""
    LOAD = "load"
    CHAOS = "chaos"
    AVAILABILITY = "availability"
    LATENCY = "latency"


@dataclass
class GeneratedTest:
    """Represents a generated test with its metadata and content."""
    name: str
    test_type: TestType
    derived_from: str
    content: str
    file_extension: str


def parse_duration(duration_str: str) -> int:
    """
    Parse a duration string in formats like "200ms", "1s", "5m" into milliseconds.

    Args:
        duration_str: Duration string (e.g., "200ms", "1s", "5m", "2h")

    Returns:
        Duration in milliseconds

    Raises:
        ValueError: If duration format is invalid
    """
    if not duration_str:
        raise ValueError("Duration string cannot be empty")

    duration_str = duration_str.strip().lower()

    # Handle milliseconds with 'ms' suffix
    ms_match = re.match(r'^(\d+)ms$', duration_str)
    if ms_match:
        return int(ms_match.group(1))

    # Handle other units (s, m, h)
    match = re.match(r'^(\d+)([smh])$', duration_str)
    if match:
        value, unit = match.groups()
        value = int(value)

        unit_multipliers = {
            's': 1000,      # seconds to milliseconds
            'm': 60000,     # minutes to milliseconds
            'h': 3600000    # hours to milliseconds
        }
        return value * unit_multipliers[unit]

    # Handle bare numbers (assume milliseconds)
    if duration_str.isdigit():
        return int(duration_str)

    raise ValueError(f"Invalid duration format: {duration_str}")


def parse_throughput(throughput_str: str) -> int:
    """
    Parse a throughput string in format like "100rps" into numeric value.

    Args:
        throughput_str: Throughput string (e.g., "100rps", "500/s")

    Returns:
        Throughput as integer requests per second

    Raises:
        ValueError: If throughput format is invalid
    """
    if not throughput_str:
        raise ValueError("Throughput string cannot be empty")

    throughput_str = throughput_str.strip().lower()

    # Handle "rps" suffix
    match = re.match(r'^(\d+)\s*rps$', throughput_str)
    if match:
        return int(match.group(1))

    # Handle "/s" suffix
    match = re.match(r'^(\d+)\s*/s$', throughput_str)
    if match:
        return int(match.group(1))

    # Handle bare numbers
    if throughput_str.isdigit():
        return int(throughput_str)

    raise ValueError(f"Invalid throughput format: {throughput_str}")


def write_tests(tests: List[GeneratedTest], output_dir: Path) -> List[Path]:
    """
    Write generated tests to files.

    Args:
        tests: List of generated tests
        output_dir: Directory to write test files to

    Returns:
        List of paths to written files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []

    for test in tests:
        filename = f"{test.name}{test.file_extension}"
        filepath = output_dir / filename
        filepath.write_text(test.content)
        written.append(filepath)

    return written


class SLOTestGenerator:
    """Generates SLO-driven load and chaos tests from ProjectContext specifications."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the SLO test generator.

        Args:
            templates_dir: Optional custom templates directory (reserved for future use)
        """
        self.templates_dir = templates_dir

    def generate(
        self,
        project_id: str,
        spec: Dict[str, Any],
        test_types: Optional[List[TestType]] = None
    ) -> List[GeneratedTest]:
        """
        Generate tests based on ProjectContext specification.

        Args:
            project_id: Unique identifier for the project
            spec: ProjectContext specification dictionary
            test_types: List of test types to generate (default: all)

        Returns:
            List of generated tests
        """
        if test_types is None:
            test_types = list(TestType)

        tests = []
        requirements = spec.get("requirements", {})
        targets = spec.get("targets", [])
        business = spec.get("business", {})

        # Get service endpoint from targets
        endpoint = self._get_service_endpoint(targets, spec)

        # Generate requested test types
        if TestType.LOAD in test_types:
            if requirements.get("throughput"):
                tests.append(self._generate_load_test(project_id, requirements, endpoint))

        if TestType.LATENCY in test_types:
            if requirements.get("latencyP99") or requirements.get("latencyP50"):
                tests.append(self._generate_latency_test(project_id, requirements, endpoint))

        if TestType.CHAOS in test_types or TestType.AVAILABILITY in test_types:
            if requirements.get("availability"):
                tests.extend(self._generate_chaos_tests(project_id, requirements, targets, business))

        return tests

    def _get_service_endpoint(self, targets: List[Dict[str, Any]], spec: Dict[str, Any]) -> str:
        """
        Extract service endpoint from targets configuration.

        Args:
            targets: List of service/deployment targets
            spec: Full ProjectContext specification

        Returns:
            Service endpoint URL
        """
        for target in targets:
            if target.get("kind") == "Service":
                ns = target.get("namespace", "default")
                name = target.get("name", "service")
                port = target.get("port", 80)
                return f"http://{name}.{ns}.svc.cluster.local:{port}"

        # Fallback: use first target name
        if targets:
            name = targets[0].get("name", "service")
            ns = targets[0].get("namespace", "default")
            return f"http://{name}.{ns}.svc.cluster.local"

        return "http://localhost:8080"

    def _generate_latency_test(
        self,
        project_id: str,
        requirements: Dict[str, Any],
        endpoint: str
    ) -> GeneratedTest:
        """Generate k6 latency test focused on response time validation."""
        p99_ms = parse_duration(requirements.get("latencyP99", "500ms"))
        p50_ms = parse_duration(requirements.get("latencyP50", "100ms"))
        error_budget = float(requirements.get("errorBudget", "0.01"))
        throughput = parse_throughput(requirements.get("throughput", "100rps"))

        k6_script = f'''// Generated from ProjectContext: {project_id}
// Derived from: requirements.latencyP99, requirements.latencyP50

import http from 'k6/http';
import {{ check, sleep }} from 'k6';
import {{ Rate, Trend }} from 'k6/metrics';

const errorRate = new Rate('errors');
const latencyTrend = new Trend('custom_latency');

export const options = {{
  thresholds: {{
    'http_req_duration': ['p(99)<{p99_ms}', 'p(50)<{p50_ms}'],
    'errors': ['rate<{error_budget}'],
    'custom_latency': ['p(99)<{p99_ms}'],
  }},
  scenarios: {{
    latency_test: {{
      executor: 'ramping-vus',
      stages: [
        {{ duration: '1m', target: {throughput // 2} }},
        {{ duration: '3m', target: {throughput} }},
        {{ duration: '2m', target: {throughput * 2} }},
        {{ duration: '2m', target: {throughput} }},
        {{ duration: '1m', target: 0 }},
      ],
    }},
  }},
}};

export default function () {{
  const response = http.get('{endpoint}/health');
  latencyTrend.add(response.timings.duration);

  const result = check(response, {{
    'status is 200': (r) => r.status === 200,
    'latency P99 OK': (r) => r.timings.duration < {p99_ms},
    'latency P50 OK': (r) => r.timings.duration < {p50_ms},
  }});

  errorRate.add(!result);
  sleep(1);
}}

export function handleSummary(data) {{
  return {{
    'stdout': JSON.stringify({{
      project: '{project_id}',
      test_type: 'latency_slo',
      p99_threshold_ms: {p99_ms},
      p50_threshold_ms: {p50_ms},
      passed: data.metrics.http_req_duration.values['p(99)'] < {p99_ms},
      actual_p99_ms: data.metrics.http_req_duration.values['p(99)'],
      actual_p50_ms: data.metrics.http_req_duration.values['p(50)'],
    }}, null, 2),
  }};
}}
'''
        return GeneratedTest(
            name=f"{project_id}-latency-slo-test",
            test_type=TestType.LATENCY,
            derived_from=f"requirements.latencyP99={requirements.get('latencyP99', '500ms')}, "
                        f"requirements.latencyP50={requirements.get('latencyP50', '100ms')}",
            content=k6_script,
            file_extension=".js"
        )

    def _generate_load_test(
        self,
        project_id: str,
        requirements: Dict[str, Any],
        endpoint: str
    ) -> GeneratedTest:
        """Generate k6 load test with constant-arrival-rate and spike scenarios."""
        throughput = parse_throughput(requirements.get("throughput", "100rps"))
        p99_ms = parse_duration(requirements.get("latencyP99", "500ms"))
        error_budget = float(requirements.get("errorBudget", "0.01"))

        spike_throughput = throughput * 3
        min_vus = max(10, throughput // 10)

        k6_script = f'''// Generated from ProjectContext: {project_id}
// Derived from: requirements.throughput, requirements.errorBudget

import http from 'k6/http';
import {{ check, sleep }} from 'k6';
import {{ Rate, Counter }} from 'k6/metrics';

const errorRate = new Rate('error_rate');
const requestCount = new Counter('requests');

export const options = {{
  scenarios: {{
    sustained_load: {{
      executor: 'constant-arrival-rate',
      rate: {throughput},
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: {min_vus},
      maxVUs: {throughput},
    }},
    spike_test: {{
      executor: 'ramping-arrival-rate',
      startRate: {throughput},
      timeUnit: '1s',
      stages: [
        {{ duration: '1m', target: {throughput} }},
        {{ duration: '30s', target: {spike_throughput} }},
        {{ duration: '1m', target: {throughput} }},
      ],
      preAllocatedVUs: {throughput},
      maxVUs: {spike_throughput},
      startTime: '5m30s',
    }},
  }},
  thresholds: {{
    'error_rate': ['rate<{error_budget}'],
    'http_req_duration': ['p(95)<{p99_ms}'],
  }},
}};

export default function () {{
  const res = http.get('{endpoint}/health');

  const passed = check(res, {{
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  }});

  errorRate.add(!passed);
  requestCount.add(1);
}}

export function handleSummary(data) {{
  const actualErrorRate = data.metrics.error_rate?.values?.rate || 0;
  return {{
    'stdout': JSON.stringify({{
      project: '{project_id}',
      test_type: 'throughput_slo',
      target_rps: {throughput},
      error_budget: {error_budget},
      passed: actualErrorRate < {error_budget},
      actual_error_rate: actualErrorRate,
      total_requests: data.metrics.requests?.values?.count || 0,
    }}, null, 2),
  }};
}}
'''
        return GeneratedTest(
            name=f"{project_id}-throughput-slo-test",
            test_type=TestType.LOAD,
            derived_from=f"requirements.throughput={requirements.get('throughput', '100rps')}, "
                        f"requirements.errorBudget={requirements.get('errorBudget', '0.01')}",
            content=k6_script,
            file_extension=".js"
        )

    def _generate_chaos_tests(
        self,
        project_id: str,
        requirements: Dict[str, Any],
        targets: List[Dict[str, Any]],
        business: Dict[str, Any]
    ) -> List[GeneratedTest]:
        """Generate chaos-mesh YAML tests based on business criticality."""
        tests = []
        criticality = business.get("criticality", "low").lower()

        # Find deployment target
        deployment_target = None
        namespace = "default"
        for target in targets:
            if target.get("kind") == "Deployment":
                deployment_target = target.get("name")
                namespace = target.get("namespace", "default")
                break

        if not deployment_target:
            # Fallback to first target
            if targets:
                deployment_target = targets[0].get("name")
                namespace = targets[0].get("namespace", "default")
            else:
                return tests

        # Pod failure test (always generated for availability requirements)
        pod_chaos_yaml = f'''# Generated from ProjectContext: {project_id}
# Derived from: requirements.availability ({requirements.get('availability', 'N/A')})
# Validates service survives pod failure

apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: {project_id}-pod-failure
  namespace: {namespace}
  labels:
    contextcore.io/project: "{project_id}"
    contextcore.io/test-type: "availability"
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces:
      - {namespace}
    labelSelectors:
      app: {deployment_target}
  duration: "30s"
'''
        tests.append(GeneratedTest(
            name=f"{project_id}-pod-failure-chaos",
            test_type=TestType.CHAOS,
            derived_from="requirements.availability",
            content=pod_chaos_yaml,
            file_extension=".yaml"
        ))

        # Network delay test (for critical/high criticality)
        if criticality in ["critical", "high"]:
            network_chaos_yaml = f'''# Generated from ProjectContext: {project_id}
# Derived from: requirements.availability, business.criticality ({criticality})
# Validates service handles network degradation gracefully

apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: {project_id}-network-delay
  namespace: {namespace}
  labels:
    contextcore.io/project: "{project_id}"
    contextcore.io/test-type: "latency-resilience"
spec:
  action: delay
  mode: all
  selector:
    namespaces:
      - {namespace}
    labelSelectors:
      app: {deployment_target}
  delay:
    latency: "100ms"
    jitter: "50ms"
    correlation: "50"
  duration: "2m"
'''
            tests.append(GeneratedTest(
                name=f"{project_id}-network-delay-chaos",
                test_type=TestType.CHAOS,
                derived_from="requirements.availability, business.criticality",
                content=network_chaos_yaml,
                file_extension=".yaml"
            ))

        # CPU stress test (for critical criticality only)
        if criticality == "critical":
            stress_chaos_yaml = f'''# Generated from ProjectContext: {project_id}
# Derived from: business.criticality (critical)
# Validates service degrades gracefully under CPU pressure

apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: {project_id}-cpu-stress
  namespace: {namespace}
  labels:
    contextcore.io/project: "{project_id}"
    contextcore.io/test-type: "resource-resilience"
spec:
  mode: one
  selector:
    namespaces:
      - {namespace}
    labelSelectors:
      app: {deployment_target}
  stressors:
    cpu:
      workers: 2
      load: 80
  duration: "2m"
'''
            tests.append(GeneratedTest(
                name=f"{project_id}-cpu-stress-chaos",
                test_type=TestType.CHAOS,
                derived_from="business.criticality",
                content=stress_chaos_yaml,
                file_extension=".yaml"
            ))

        return tests
