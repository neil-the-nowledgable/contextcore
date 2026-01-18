# ContextCore Operator Fix Instructions

Use this prompt in a Claude Code session to fix the identified issues.

---

## Context

The ContextCore Kubernetes operator at `src/contextcore/operator.py` is fully implemented but has configuration mismatches that prevent deployment.

## Issues to Fix

### 1. API Version Mismatch (Critical)

**Problem**: The operator watches `v1alpha1` but the source CRD defines `v1`.

**Files involved**:
- `src/contextcore/operator.py` (lines 668, 761, 836) - watches `v1alpha1`
- `crds/projectcontext.yaml` - defines `v1` as storage version

**Fix options**:
- **Option A (Recommended)**: Add `v1alpha1` as a served version in `crds/projectcontext.yaml` for development compatibility
- **Option B**: Update operator.py to watch `v1` and adapt to the richer schema

### 2. CRD Schema Divergence (Critical)

**Problem**: Operator expects simplified flat schema but source CRD has nested structure.

| Operator expects | Source CRD has |
|------------------|----------------|
| `spec.project` (string) | `spec.project.id` (nested object) |
| `spec.service` (string) | `spec.targets[].name` (array) |
| `spec.criticality` (string) | `spec.business.criticality` (nested) |
| `spec.owner` (string) | `spec.business.owner` (nested) |

**Fix**: Update `src/contextcore/operator.py` artifact generators to handle both schemas:

```python
# Example fix for project_id extraction
def get_project_id(spec: Dict[str, Any], default: str) -> str:
    """Extract project ID from v1 or v1alpha1 schema."""
    project = spec.get("project")
    if isinstance(project, dict):
        return project.get("id", default)  # v1 schema
    return project or default  # v1alpha1 schema

def get_service_name(spec: Dict[str, Any], default: str) -> str:
    """Extract service name from v1 or v1alpha1 schema."""
    # v1alpha1: direct service field
    if "service" in spec:
        return spec["service"]
    # v1: first target name
    targets = spec.get("targets", [])
    if targets:
        return targets[0].get("name", default)
    return default

def get_criticality(spec: Dict[str, Any]) -> str:
    """Extract criticality from v1 or v1alpha1 schema."""
    # v1alpha1: top-level
    if "criticality" in spec:
        return spec["criticality"]
    # v1: nested in business
    return spec.get("business", {}).get("criticality", "medium")
```

### 3. Deployment Mount Path (Medium)

**Problem**: The deployment mounts `/src/contextcore` to `/app` but kopf expects `/app/operator.py`.

**File**: `~/Documents/Deploy/contextcore/operator/deployment.yaml`

**Current** (line 34):
```yaml
kopf run /app/operator.py --verbose
```

**Current mount** (line 71):
```yaml
hostPath:
  path: /src/contextcore
```

After Kind extraMounts, the structure is:
- `/src/contextcore/` contains the ContextCore repo
- Operator file is at `/src/contextcore/src/contextcore/operator.py`

**Fix**: Update the kopf run command:
```yaml
args:
  - |
    pip install --quiet kopf kubernetes opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp requests &&
    kopf run /app/src/contextcore/operator.py --verbose --liveness=http://0.0.0.0:8080/healthz
```

### 4. Enable Operator in Kustomization (Medium)

**Problem**: `~/Documents/Deploy/contextcore/kustomization.yaml` has `resources: []`

**Fix**: After fixing issues 1-3, update to:
```yaml
resources:
  - crds/projectcontext.yaml
  - operator/deployment.yaml
  - operator/rbac.yaml
```

### 5. Hardcoded Metric Names (Low)

**Problem**: Operator assumes `http_requests_total` and `http_request_duration_seconds_bucket` metric names.

**File**: `src/contextcore/operator.py` (lines 325-331, 429, 462, 483, 503)

**Fix**: Add metric name configuration to CRD spec:
```yaml
spec:
  observability:
    metrics:
      requestsTotal: "http_requests_total"
      durationBucket: "http_request_duration_seconds_bucket"
```

Then update generators to use configurable names:
```python
def generate_prometheus_rules(...):
    obs = spec.get("observability", {})
    metrics = obs.get("metrics", {})
    requests_metric = metrics.get("requestsTotal", "http_requests_total")
    duration_metric = metrics.get("durationBucket", "http_request_duration_seconds_bucket")
    # Use these in PromQL expressions
```

---

## Verification Steps

After applying fixes:

1. **Validate CRD**:
   ```bash
   kubectl apply --dry-run=client -f crds/projectcontext.yaml
   ```

2. **Test operator locally**:
   ```bash
   cd ~/Documents/dev/ContextCore
   kopf run src/contextcore/operator.py --verbose --namespace=contextcore
   ```

3. **Apply test ProjectContext**:
   ```bash
   kubectl apply -f demo/projectcontexts/frontend.yaml
   ```

4. **Check generated artifacts**:
   ```bash
   kubectl get servicemonitors,prometheusrules,configmaps -l contextcore.io/managed-by=contextcore-operator
   ```

5. **Verify traces in Tempo**:
   - Open Grafana at http://localhost:3000
   - Navigate to Explore > Tempo
   - Search for `service.name = "contextcore-operator"`

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/contextcore/operator.py` | Add schema compatibility helpers, use them in generators |
| `crds/projectcontext.yaml` | Add v1alpha1 version for backwards compatibility |
| `~/Documents/Deploy/contextcore/operator/deployment.yaml` | Fix kopf run path |
| `~/Documents/Deploy/contextcore/kustomization.yaml` | Enable resources |

---

## Prompt for Claude

```
Fix the ContextCore operator configuration issues:

1. Update src/contextcore/operator.py to handle both v1 and v1alpha1 CRD schemas by adding helper functions that extract project_id, service_name, criticality, and owner from either nested (v1) or flat (v1alpha1) structures.

2. Update crds/projectcontext.yaml to serve both v1 (storage) and v1alpha1 (served but not storage) for backwards compatibility.

3. Fix ~/Documents/Deploy/contextcore/operator/deployment.yaml to use the correct path: /app/src/contextcore/operator.py

4. Update ~/Documents/Deploy/contextcore/kustomization.yaml to include the CRD and operator resources.

Reference files:
- Operator: ~/Documents/dev/ContextCore/src/contextcore/operator.py
- Source CRD: ~/Documents/dev/ContextCore/crds/projectcontext.yaml
- Deploy CRD: ~/Documents/Deploy/contextcore/crds/projectcontext.yaml
- Deployment: ~/Documents/Deploy/contextcore/operator/deployment.yaml
- Kustomization: ~/Documents/Deploy/contextcore/kustomization.yaml
```
