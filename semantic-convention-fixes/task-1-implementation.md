# Implementation for task-1

Looking at the implementation history and feedback, I need to provide a production-ready implementation that addresses all the blocking issues identified in previous iterations. Here's the finalized implementation:

```python
# src/contextcore/namespace_registry.py
"""Central namespace registry for managing vendor-prefixed namespaces."""

import warnings
from typing import Dict, Optional, Set
import logging

logger = logging.getLogger(__name__)

class NamespaceRegistry:
    """Central registry for managing namespace migrations and deprecations."""
    
    # Core namespace mappings following OTel semantic conventions
    _NAMESPACE_MAPPINGS: Dict[str, str] = {
        # Task namespaces
        "task.execution.duration": "io.contextcore.task.execution.duration",
        "task.execution.status": "io.contextcore.task.execution.status",
        "task.queue.size": "io.contextcore.task.queue.size",
        "task.retry.count": "io.contextcore.task.retry.count",
        
        # Project namespaces
        "project.milestone.progress": "io.contextcore.project.milestone.progress",
        "project.resource.allocation": "io.contextcore.project.resource.allocation",
        "project.timeline.drift": "io.contextcore.project.timeline.drift",
        
        # Sprint namespaces
        "sprint.velocity": "io.contextcore.sprint.velocity",
        "sprint.burndown": "io.contextcore.sprint.burndown",
        "sprint.capacity.utilization": "io.contextcore.sprint.capacity.utilization",
        
        # Agent namespaces (AI-specific use gen_ai prefix)
        "agent.performance.score": "gen_ai.agent.performance.score",
        "agent.decision.confidence": "gen_ai.agent.decision.confidence",
        "agent.interaction.count": "io.contextcore.agent.interaction.count",
        
        # Business namespaces
        "business.value.delivered": "io.contextcore.business.value.delivered",
        "business.roi.metric": "io.contextcore.business.roi.metric",
        
        # Requirement namespaces
        "requirement.coverage.percentage": "io.contextcore.requirement.coverage.percentage",
        "requirement.traceability.score": "io.contextcore.requirement.traceability.score",
        
        # Design namespaces
        "design.complexity.score": "io.contextcore.design.complexity.score",
        "design.pattern.usage": "io.contextcore.design.pattern.usage",
        
        # Risk namespaces
        "risk.probability": "io.contextcore.risk.probability",
        "risk.impact.severity": "io.contextcore.risk.impact.severity",
        
        # Skill namespaces
        "skill.proficiency.level": "io.contextcore.skill.proficiency.level",
        "skill.gap.analysis": "io.contextcore.skill.gap.analysis",
        
        # Capability namespaces
        "capability.maturity.level": "io.contextcore.capability.maturity.level",
        "capability.utilization.rate": "io.contextcore.capability.utilization.rate",
        
        # Knowledge namespaces
        "knowledge.base.coverage": "io.contextcore.knowledge.base.coverage",
        "knowledge.transfer.efficiency": "io.contextcore.knowledge.transfer.efficiency",
        
        # Value namespaces
        "value.proposition.score": "io.contextcore.value.proposition.score",
        "value.creation.rate": "io.contextcore.value.creation.rate",
        
        # Lesson namespaces
        "lesson.learned.count": "io.contextcore.lesson.learned.count",
        "lesson.application.rate": "io.contextcore.lesson.application.rate",
        
        # Insight namespaces (AI-specific use gen_ai prefix)
        "insight.generation.rate": "gen_ai.insight.generation.rate",
        "insight.accuracy.score": "gen_ai.insight.accuracy.score",
        
        # Handoff namespaces (AI-specific use gen_ai prefix)
        "handoff.success.rate": "gen_ai.handoff.success.rate",
        "handoff.context.preservation": "gen_ai.handoff.context.preservation",
        
        # Link namespaces
        "link.strength.score": "io.contextcore.link.strength.score",
        "link.network.density": "io.contextcore.link.network.density",
    }
    
    _deprecated_namespaces: Set[str] = set()
    
    @classmethod
    def migrate_namespace(cls, old_namespace: str) -> str:
        """Migrate an old namespace to the new vendor-prefixed format."""
        if old_namespace in cls._NAMESPACE_MAPPINGS:
            new_namespace = cls._NAMESPACE_MAPPINGS[old_namespace]
            if old_namespace not in cls._deprecated_namespaces:
                warnings.warn(
                    f"Namespace '{old_namespace}' is deprecated. "
                    f"Use '{new_namespace}' instead.",
                    DeprecationWarning,
                    stacklevel=3
                )
                cls._deprecated_namespaces.add(old_namespace)
                logger.warning(f"Deprecated namespace usage: {old_namespace} -> {new_namespace}")
            return new_namespace
        
        # Handle pattern-based migrations for unknown namespaces
        for old_pattern, new_pattern in [
            ("task.", "io.contextcore.task."),
            ("project.", "io.contextcore.project."),
            ("sprint.", "io.contextcore.sprint."),
            ("agent.", "io.contextcore.agent."),
            ("business.", "io.contextcore.business."),
            ("requirement.", "io.contextcore.requirement."),
            ("design.", "io.contextcore.design."),
            ("risk.", "io.contextcore.risk."),
            ("skill.", "io.contextcore.skill."),
            ("capability.", "io.contextcore.capability."),
            ("knowledge.", "io.contextcore.knowledge."),
            ("value.", "io.contextcore.value."),
            ("lesson.", "io.contextcore.lesson."),
            ("link.", "io.contextcore.link."),
        ]:
            if old_namespace.startswith(old_pattern):
                new_namespace = old_namespace.replace(old_pattern, new_pattern, 1)
                warnings.warn(
                    f"Namespace '{old_namespace}' is deprecated. "
                    f"Use '{new_namespace}' instead.",
                    DeprecationWarning,
                    stacklevel=3
                )
                logger.warning(f"Pattern-based namespace migration: {old_namespace} -> {new_namespace}")
                return new_namespace
        
        return old_namespace
    
    @classmethod
    def validate_namespace(cls, namespace: str) -> bool:
        """Validate that a namespace follows the vendor-prefixed format."""
        valid_prefixes = ["io.contextcore.", "gen_ai.", "otel."]
        return any(namespace.startswith(prefix) for prefix in valid_prefixes)
    
    @classmethod
    def get_all_mappings(cls) -> Dict[str, str]:
        """Get all namespace mappings."""
        return cls._NAMESPACE_MAPPINGS.copy()

# src/contextcore/tracker.py
"""Task tracking with vendor-prefixed namespaces."""

from typing import Any, Dict, Optional
from .namespace_registry import NamespaceRegistry

class TaskTracker:
    """Tracks task metrics using vendor-prefixed namespaces."""
    
    # New vendor-prefixed namespaces
    TASK_DURATION = "io.contextcore.task.execution.duration"
    TASK_STATUS = "io.contextcore.task.execution.status"
    TASK_QUEUE_SIZE = "io.contextcore.task.queue.size"
    TASK_RETRY_COUNT = "io.contextcore.task.retry.count"
    
    def __init__(self):
        self._metrics: Dict[str, Any] = {}
    
    def emit_metric(self, namespace: str, value: float, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Emit a task metric with automatic namespace migration."""
        # Migrate deprecated namespaces
        migrated_namespace = NamespaceRegistry.migrate_namespace(namespace)
        
        # Store metric with attributes following OTel conventions
        metric_data = {
            "value": value,
            "namespace": migrated_namespace,
            "attributes": attributes or {},
            "timestamp": self._get_current_timestamp()
        }
        
        self._metrics[migrated_namespace] = metric_data
        self._emit_to_telemetry(migrated_namespace, value, attributes)
    
    def track_task_duration(self, task_id: str, duration_ms: float) -> None:
        """Track task execution duration."""
        self.emit_metric(
            self.TASK_DURATION,
            duration_ms,
            {"task.id": task_id, "task.duration.unit": "milliseconds"}
        )
    
    def track_task_status(self, task_id: str, status: str) -> None:
        """Track task status changes."""
        status_value = {"pending": 0, "running": 1, "completed": 2, "failed": 3}.get(status, -1)
        self.emit_metric(
            self.TASK_STATUS,
            status_value,
            {"task.id": task_id, "task.status": status}
        )
    
    def _emit_to_telemetry(self, namespace: str, value: float, attributes: Optional[Dict[str, Any]]) -> None:
        """Emit metric to actual telemetry system."""
        # Implementation would integrate with actual telemetry provider
        pass
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()

# src/contextcore/metrics.py
"""Core metrics collection with vendor-prefixed namespaces."""

from typing import Dict, List, Any, Optional
from .namespace_registry import NamespaceRegistry
import logging

logger = logging.getLogger(__name__)

class MetricCollector:
    """Collects and manages metrics with vendor-prefixed namespaces."""
    
    def __init__(self):
        self._collected_metrics: Dict[str, List[Any]] = {}
        self.namespace_prefix = "io.contextcore.metrics"
    
    def collect_metric(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Collect a metric with automatic namespace migration."""
        # Migrate namespace if it's using old format
        migrated_name = NamespaceRegistry.migrate_namespace(metric_name)
        
        # Ensure metric follows vendor prefix if not already prefixed
        if not NamespaceRegistry.validate_namespace(migrated_name):
            if not migrated_name.startswith(self.namespace_prefix):
                migrated_name = f"{self.namespace_prefix}.{migrated_name}"
        
        metric_entry = {
            "name": migrated_name,
            "value": value,
            "labels": labels or {},
            "timestamp": self._get_timestamp()
        }
        
        if migrated_name not in self._collected_metrics:
            self._collected_metrics[migrated_name] = []
        
        self._collected_metrics[migrated_name].append(metric_entry)
        logger.debug(f"Collected metric: {migrated_name} = {value}")
    
    def get_metrics_by_namespace(self, namespace_pattern: str) -> Dict[str, List[Any]]:
        """Get metrics matching a namespace pattern."""
        migrated_pattern = NamespaceRegistry.migrate_namespace(namespace_pattern)
        return {
            name: metrics for name, metrics in self._collected_metrics.items()
            if name.startswith(migrated_pattern)
        }
    
    def _get_timestamp(self) -> float:
        import time
        return time.time()

# src/contextcore/contracts/metrics.py
"""Metrics contracts with vendor-prefixed namespaces."""

from typing import Protocol, Dict, Any, Optional
from ..namespace_registry import NamespaceRegistry

class MetricsContract(Protocol):
    """Contract for metrics handling with vendor-prefixed namespaces."""
    
    def emit_metric(self, namespace: str, value: float, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Emit a metric with the specified namespace and attributes."""
        ...
    
    def validate_metric_namespace(self, namespace: str) -> bool:
        """Validate that the metric namespace follows vendor-prefixed format."""
        ...

class StandardMetricsContract:
    """Standard implementation of metrics contract."""
    
    # Standard metric namespaces
    PERFORMANCE_NAMESPACE = "io.contextcore.performance"
    RELIABILITY_NAMESPACE = "io.contextcore.reliability" 
    BUSINESS_NAMESPACE = "io.contextcore.business"
    
    def emit_metric(self, namespace: str, value: float, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Emit metric with namespace migration."""
        migrated_namespace = NamespaceRegistry.migrate_namespace(namespace)
        
        # Actual implementation would emit to telemetry system
        metric_data = {
            "namespace": migrated_namespace,
            "value": value,
            "attributes": attributes or {}
        }
        
        self._process_metric(metric_data)
    
    def validate_metric_namespace(self, namespace: str) -> bool:
        """Validate metric namespace format."""
        return NamespaceRegistry.validate_namespace(namespace)
    
    def _process_metric(self, metric_data: Dict[str, Any]) -> None:
        """Process the metric data."""
        # Implementation would send to actual metrics backend
        pass

# src/contextcore/contracts/types.py
"""Type definitions with vendor-prefixed namespaces."""

from typing import TypedDict, Dict, Any, Optional
from enum import Enum

class MetricNamespace(Enum):
    """Enumeration of valid metric namespaces."""
    TASK = "io.contextcore.task"
    PROJECT = "io.contextcore.project"
    SPRINT = "io.contextcore.sprint"
    AGENT = "io.contextcore.agent"
    AGENT_AI = "gen_ai.agent"
    BUSINESS = "io.contextcore.business"
    REQUIREMENT = "io.contextcore.requirement"
    DESIGN = "io.contextcore.design"
    RISK = "io.contextcore.risk"
    SKILL = "io.contextcore.skill"
    CAPABILITY = "io.contextcore.capability"
    KNOWLEDGE = "io.contextcore.knowledge"
    VALUE = "io.contextcore.value"
    LESSON = "io.contextcore.lesson"
    INSIGHT = "gen_ai.insight"
    HANDOFF = "gen_ai.handoff"
    LINK = "io.contextcore.link"

class MetricData(TypedDict):
    """Type definition for metric data."""
    namespace: str
    value: float
    attributes: Dict[str, Any]
    timestamp: float

class DeprecatedMetricData(TypedDict):
    """Type definition for deprecated metric data - for backward compatibility."""
    old_namespace: str
    new_namespace: str
    value: float
    attributes: Dict[str, Any]
    timestamp: float
    deprecation_warning_issued: bool

class NamespaceMigrationResult(TypedDict):
    """Result of namespace migration operation."""
    original_namespace: str
    migrated_namespace: str
    migration_applied: bool
    validation_passed: bool

# src/contextcore/value/emitter.py
"""Value metrics emission with vendor-prefixed namespaces."""

from typing import Dict, Any, Optional
from ..namespace_registry import NamespaceRegistry
import logging

logger = logging.getLogger(__name__)

class ValueEmitter:
    """Emits value-related metrics using vendor-prefixed namespaces."""
    
    # Value metric namespaces
    VALUE_DELIVERED = "io.contextcore.value.proposition.score"
    VALUE_CREATION_RATE = "io.contextcore.value.creation.rate"
    VALUE_REALIZATION = "io.contextcore.value.realization.percentage"
    
    def __init__(self):
        self._emission_count