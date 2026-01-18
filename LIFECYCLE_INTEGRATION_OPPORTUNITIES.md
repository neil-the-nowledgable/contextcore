# ContextCore: Lifecycle-Wide Metadata Integration Opportunities

## Executive Summary

ContextCore's core thesis - **"Context is Infrastructure"** - provides a unified metadata layer that can drive automation across the entire software lifecycle. The current implementation focuses on operations (deriving ServiceMonitors, PrometheusRules, Dashboards). This document identifies high-value opportunities to extend the metadata abstraction into design, development, and testing phases.

**Key Insight**: The ProjectContext CRD already captures sufficient metadata to drive automation in phases where it's currently unused. The gap isn't in the schema - it's in the tooling that consumes it.

---

## Current State vs. Opportunity

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SOFTWARE LIFECYCLE                                    │
├─────────────┬─────────────┬─────────────┬─────────────┬────────────────────┤
│   DESIGN    │ DEVELOPMENT │   TESTING   │  DEPLOYMENT │    OPERATIONS      │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────────────┤
│             │             │             │             │                    │
│  ○ ADRs     │  ○ Commits  │  ○ Tests    │  ○ Releases │  ● ServiceMonitor  │
│  ○ Specs    │  ○ PRs      │  ○ Coverage │  ○ Configs  │  ● PrometheusRule  │
│  ○ Diagrams │  ○ Reviews  │  ○ Load     │  ○ Rollouts │  ● Dashboards      │
│             │             │             │             │                    │
│  UNTAPPED   │  UNTAPPED   │  UNTAPPED   │  PARTIAL    │  IMPLEMENTED       │
└─────────────┴─────────────┴─────────────┴─────────────┴────────────────────┘

● = Currently implemented    ○ = Opportunity for metadata-driven automation
```

---

## Phase 1: Design Integration

### 1.1 Requirements → Test Matrix Generation

**Metadata Used**:
- `requirements.availability` → Chaos engineering scenarios
- `requirements.latency_p99` → Load test thresholds
- `requirements.errorBudget` → Acceptable failure rates
- `risks[].type` → Test category prioritization

**Implementation**:
```python
# New CLI command: contextcore generate tests
def generate_test_matrix(project_context: ProjectContextSpec) -> TestMatrix:
    """Generate test matrix from requirements and risks."""
    tests = []

    # Availability → Chaos tests
    if req := project_context.requirements:
        if req.availability:
            availability_pct = float(req.availability)
            if availability_pct >= 99.9:
                tests.append(ChaosTest(
                    name="pod-failure-recovery",
                    scenario="Kill 1 pod, verify recovery < 30s",
                    derived_from="requirements.availability"
                ))
                tests.append(ChaosTest(
                    name="network-partition",
                    scenario="Isolate service, verify graceful degradation",
                    derived_from="requirements.availability"
                ))

    # Latency → Load tests
    if req and req.latency_p99:
        threshold_ms = parse_duration(req.latency_p99)
        tests.append(LoadTest(
            name="latency-under-load",
            threshold_p99_ms=threshold_ms,
            concurrent_users=100,  # Could derive from throughput
            derived_from="requirements.latency_p99"
        ))

    # Risks → Security/Compliance tests
    for risk in project_context.risks:
        if risk.type == RiskType.SECURITY:
            tests.append(SecurityTest(
                name=f"security-{risk.description[:20]}",
                controls=risk.controls,
                priority=risk.priority,
                derived_from=f"risks[{risk.type}]"
            ))

    return TestMatrix(tests=tests)
```

**Output**: Test specification YAML that integrates with pytest, k6, chaos-mesh.

---

### 1.2 ADR → Code Constraint Validation

**Metadata Used**:
- `design.adr` → ADR document URL/ID
- `agentGuidance.constraints` → Extracted decisions as rules

**Concept**: Parse ADR documents to extract architectural decisions, then generate linting rules or pre-commit hooks that enforce them.

**Implementation**:
```python
# ADR Parser that extracts constraints
class ADRConstraintExtractor:
    """Extract enforceable constraints from ADR documents."""

    def extract(self, adr_content: str) -> List[ConstraintSpec]:
        """
        Parse ADR markdown to find:
        - "We will use X" → Enforce X usage
        - "We will NOT use Y" → Block Y usage
        - "All Z must have W" → Require W for Z
        """
        constraints = []

        # Pattern: "We will use {technology} for {purpose}"
        for match in re.finditer(r"[Ww]e will use (\w+)", adr_content):
            constraints.append(ConstraintSpec(
                id=f"adr-require-{match.group(1).lower()}",
                rule=f"Use {match.group(1)} as specified in ADR",
                severity=ConstraintSeverity.WARNING,
                source="design.adr"
            ))

        # Pattern: "We will NOT use {technology}"
        for match in re.finditer(r"[Ww]e will [Nn][Oo][Tt] use (\w+)", adr_content):
            constraints.append(ConstraintSpec(
                id=f"adr-forbid-{match.group(1).lower()}",
                rule=f"Do not use {match.group(1)} - see ADR",
                severity=ConstraintSeverity.BLOCKING,
                source="design.adr"
            ))

        return constraints

# Auto-populate agentGuidance.constraints from ADR
def sync_adr_constraints(project_id: str):
    """Sync constraints from ADR to ProjectContext."""
    ctx = get_project_context(project_id)
    if ctx.spec.design and ctx.spec.design.adr:
        adr_content = fetch_adr(ctx.spec.design.adr)
        extractor = ADRConstraintExtractor()
        constraints = extractor.extract(adr_content)

        # Update ProjectContext with derived constraints
        patch_guidance_constraints(project_id, constraints)
```

**Benefit**: Architectural decisions become enforceable code constraints, not just documentation.

---

### 1.3 API Contract → Development Scaffolding

**Metadata Used**:
- `design.apiContract` → OpenAPI/AsyncAPI specification URL
- `targets[].kind` → Service type (determines implementation pattern)

**Implementation**:
```python
# New CLI: contextcore generate scaffold
def generate_scaffold(project_context: ProjectContextSpec) -> Scaffold:
    """Generate development scaffolding from API contract."""

    if not project_context.design or not project_context.design.api_contract:
        raise ValueError("No API contract specified in ProjectContext")

    spec = fetch_openapi(project_context.design.api_contract)

    scaffold = Scaffold()

    # Generate route handlers
    for path, methods in spec.paths.items():
        for method, operation in methods.items():
            scaffold.add_handler(
                path=path,
                method=method,
                operation_id=operation.operation_id,
                request_schema=operation.request_body,
                response_schema=operation.responses["200"],
            )

    # Generate mock server for development
    scaffold.add_mock_server(spec)

    # Generate client SDK
    scaffold.add_client_sdk(spec)

    # Add requirements-based middleware
    if req := project_context.requirements:
        if req.latency_p99:
            scaffold.add_middleware("timeout", timeout_ms=parse_duration(req.latency_p99) * 2)
        if req.throughput:
            scaffold.add_middleware("rate_limit", rps=parse_throughput(req.throughput))

    return scaffold
```

---

## Phase 2: Development Integration

### 2.1 Requirements-Driven Code Suggestions

**Metadata Used**:
- `requirements.throughput` → Connection pool, queue sizes
- `requirements.latency_p50` → Caching strategies
- `business.criticality` → Resilience patterns
- `requirements.availability` → Redundancy requirements

**Implementation** (IDE Plugin / Agent Guidance):
```python
class RequirementsDrivenSuggestions:
    """Generate code suggestions from ProjectContext requirements."""

    def suggest_for_database(self, ctx: ProjectContextSpec) -> List[Suggestion]:
        suggestions = []

        if req := ctx.requirements:
            # Throughput → Pool sizing
            if req.throughput:
                rps = parse_throughput(req.throughput)
                pool_size = max(10, rps // 100)  # Heuristic
                suggestions.append(Suggestion(
                    type="configuration",
                    message=f"Consider connection pool size of {pool_size} for {rps} rps throughput",
                    code=f"pool_size = {pool_size}  # Derived from requirements.throughput",
                    derived_from="requirements.throughput"
                ))

            # Latency → Read replicas / caching
            if req.latency_p50:
                latency_ms = parse_duration(req.latency_p50)
                if latency_ms < 50:
                    suggestions.append(Suggestion(
                        type="architecture",
                        message="P50 < 50ms requires caching or read replicas",
                        derived_from="requirements.latency_p50"
                    ))

        # Criticality → Circuit breaker
        if ctx.business and ctx.business.criticality == Criticality.CRITICAL:
            suggestions.append(Suggestion(
                type="resilience",
                message="Critical service should implement circuit breaker pattern",
                code="@circuit_breaker(failure_threshold=5, recovery_timeout=30)",
                derived_from="business.criticality"
            ))

        return suggestions
```

**Delivery Mechanism**:
- VSCode extension that reads ProjectContext
- Agent guidance auto-populated with suggestions
- Pre-commit hook that warns about violations

---

### 2.2 Risk-Aware Code Review Automation

**Metadata Used**:
- `risks[].type` → Review focus areas
- `risks[].controls` → Required security controls
- `risks[].priority` → Review urgency
- `targets[]` → Affected paths

**Implementation**:
```python
class RiskAwareReviewer:
    """Prioritize and focus code reviews based on ProjectContext risks."""

    def analyze_pr(self, pr: PullRequest, ctx: ProjectContextSpec) -> ReviewGuidance:
        guidance = ReviewGuidance()

        changed_paths = pr.get_changed_files()

        for risk in ctx.risks:
            # Check if PR affects risky areas
            if self._paths_overlap(changed_paths, risk.scope):
                guidance.add_focus_area(
                    area=risk.type.value,
                    reason=risk.description,
                    priority=risk.priority,
                    controls_to_verify=risk.controls,
                )

                # P1 risks require security team review
                if risk.priority == AlertPriority.P1:
                    guidance.require_reviewer("security-team")

                # Compliance risks require audit trail
                if risk.type == RiskType.COMPLIANCE:
                    guidance.require_sign_off("compliance-officer")

        # Auto-generate review checklist
        guidance.checklist = self._generate_checklist(ctx.risks, changed_paths)

        return guidance

    def _generate_checklist(self, risks: List[RiskSpec], paths: List[str]) -> List[str]:
        """Generate review checklist from risks."""
        checklist = []

        for risk in risks:
            if risk.type == RiskType.SECURITY:
                checklist.extend([
                    "[ ] No hardcoded credentials",
                    "[ ] Input validation on all user data",
                    "[ ] SQL injection protection verified",
                ])
            elif risk.type == RiskType.DATA_INTEGRITY:
                checklist.extend([
                    "[ ] Database transactions used appropriately",
                    "[ ] Idempotency keys for mutations",
                    "[ ] Data validation at boundaries",
                ])

        return checklist
```

---

### 2.3 Cost Attribution & Tagging

**Metadata Used**:
- `business.costCenter` → Cloud resource tagging
- `business.owner` → Ownership attribution
- `business.value` → Priority for cost optimization
- `targets[]` → Resources to tag

**Implementation**:
```python
# Generate Kubernetes resource annotations/labels from ProjectContext
def generate_cost_labels(ctx: ProjectContextSpec) -> Dict[str, str]:
    """Generate labels for cost attribution."""
    labels = {
        "contextcore.io/project": ctx.project.id,
    }

    if ctx.business:
        if ctx.business.cost_center:
            labels["cost-center"] = ctx.business.cost_center
        if ctx.business.owner:
            labels["owner"] = ctx.business.owner
        if ctx.business.value:
            labels["business-value"] = ctx.business.value.value
        if ctx.business.criticality:
            labels["criticality"] = ctx.business.criticality.value

    return labels

# Operator enhancement: Apply cost labels to all targets
def apply_cost_attribution(ctx: ProjectContext):
    """Apply cost labels to all target resources."""
    labels = generate_cost_labels(ctx.spec)

    for target in ctx.spec.targets:
        patch_resource_labels(
            kind=target.kind,
            name=target.name,
            namespace=target.namespace or ctx.metadata.namespace,
            labels=labels
        )
```

**Benefit**: Cloud cost reports can be grouped by business value, cost center, or criticality - derived automatically from ProjectContext.

---

## Phase 3: Testing Integration

### 3.1 SLO-Driven Test Generation

**Metadata Used**:
- `requirements.availability` → Failure injection scenarios
- `requirements.errorBudget` → Acceptable error rates
- `requirements.latency_p99` → Performance thresholds
- `business.criticality` → Test frequency/thoroughness

**Implementation**:
```python
# New CLI: contextcore generate slo-tests
class SLOTestGenerator:
    """Generate tests that verify SLO compliance."""

    def generate(self, ctx: ProjectContextSpec) -> SLOTestSuite:
        suite = SLOTestSuite(project_id=ctx.project.id)

        if req := ctx.requirements:
            # Availability SLO → Chaos tests
            if req.availability:
                target = float(req.availability)
                suite.add_test(AvailabilityTest(
                    name="availability-slo-verification",
                    target_percentage=target,
                    measurement_window="5m",
                    chaos_scenarios=[
                        "pod-kill",
                        "network-delay-100ms",
                        "cpu-stress-50pct",
                    ],
                    pass_criteria=f"Availability >= {target}% during chaos",
                ))

            # Error budget → Error rate tests
            if req.error_budget:
                budget = float(req.error_budget)
                suite.add_test(ErrorBudgetTest(
                    name="error-budget-verification",
                    max_error_rate=budget,
                    duration="1h",
                    traffic_pattern="realistic",  # Use production traffic patterns
                ))

            # Latency SLO → Performance tests
            if req.latency_p99:
                threshold_ms = parse_duration(req.latency_p99)

                # Derive load levels from throughput if available
                load_levels = [10, 50, 100]  # Default
                if req.throughput:
                    target_rps = parse_throughput(req.throughput)
                    load_levels = [
                        int(target_rps * 0.5),
                        int(target_rps * 1.0),
                        int(target_rps * 1.5),  # Over-target
                    ]

                suite.add_test(LatencyTest(
                    name="latency-slo-verification",
                    threshold_p99_ms=threshold_ms,
                    load_levels_rps=load_levels,
                    duration_per_level="2m",
                ))

        # Criticality → Test frequency
        if ctx.business and ctx.business.criticality:
            suite.schedule = self._schedule_for_criticality(ctx.business.criticality)

        return suite

    def _schedule_for_criticality(self, criticality: Criticality) -> str:
        """Determine test frequency based on criticality."""
        return {
            Criticality.CRITICAL: "*/15 * * * *",  # Every 15 minutes
            Criticality.HIGH: "0 * * * *",         # Hourly
            Criticality.MEDIUM: "0 */6 * * *",     # Every 6 hours
            Criticality.LOW: "0 0 * * *",          # Daily
        }.get(criticality, "0 0 * * *")
```

**Output**: k6 scripts, pytest fixtures, chaos-mesh experiments - all derived from ProjectContext.

---

### 3.2 Risk-Based Test Prioritization

**Metadata Used**:
- `risks[].priority` → Test execution order
- `risks[].type` → Test category selection
- `risks[].controls` → Control verification

**Implementation**:
```python
class RiskBasedTestPrioritizer:
    """Prioritize test execution based on risk profile."""

    def prioritize(self, tests: List[Test], ctx: ProjectContextSpec) -> List[Test]:
        """Sort tests by risk priority."""

        # Build risk score for each test
        scored_tests = []
        for test in tests:
            score = self._calculate_risk_score(test, ctx.risks)
            scored_tests.append((score, test))

        # Sort by score descending (highest risk first)
        scored_tests.sort(key=lambda x: x[0], reverse=True)

        return [test for _, test in scored_tests]

    def _calculate_risk_score(self, test: Test, risks: List[RiskSpec]) -> int:
        """Calculate risk score for a test."""
        score = 0

        for risk in risks:
            if self._test_covers_risk(test, risk):
                # P1 = 1000, P2 = 100, P3 = 10, P4 = 1
                priority_weight = {
                    AlertPriority.P1: 1000,
                    AlertPriority.P2: 100,
                    AlertPriority.P3: 10,
                    AlertPriority.P4: 1,
                }.get(risk.priority, 1)

                # Risk type multiplier
                type_weight = {
                    RiskType.SECURITY: 2.0,
                    RiskType.COMPLIANCE: 1.8,
                    RiskType.DATA_INTEGRITY: 1.5,
                    RiskType.AVAILABILITY: 1.3,
                    RiskType.FINANCIAL: 1.2,
                    RiskType.REPUTATIONAL: 1.0,
                }.get(risk.type, 1.0)

                score += int(priority_weight * type_weight)

        return score
```

**Integration**: pytest plugin that reorders test execution based on ProjectContext risks.

---

### 3.3 Contract Drift Detection

**Metadata Used**:
- `design.apiContract` → Expected contract
- `targets[]` → Services to verify
- `agentInsights` → Store drift findings

**Implementation**:
```python
class ContractDriftDetector:
    """Detect drift between API contract and implementation."""

    def detect(self, ctx: ProjectContextSpec) -> List[ContractDrift]:
        """Compare contract spec to runtime behavior."""

        if not ctx.design or not ctx.design.api_contract:
            return []

        spec = fetch_openapi(ctx.design.api_contract)
        drifts = []

        for path, methods in spec.paths.items():
            for method, operation in methods.items():
                # Call actual endpoint
                actual_response = self._probe_endpoint(
                    ctx.targets[0],  # Assume first target is the service
                    path,
                    method
                )

                # Compare response schema
                expected_schema = operation.responses.get("200", {}).get("schema")
                if expected_schema:
                    drift = self._compare_schemas(expected_schema, actual_response)
                    if drift:
                        drifts.append(ContractDrift(
                            path=path,
                            method=method,
                            expected=expected_schema,
                            actual=actual_response.schema,
                            differences=drift,
                        ))

        # Store findings as agent insights
        if drifts:
            emitter = InsightEmitter(project_id=ctx.project.id)
            emitter.emit_discovery(
                summary=f"Contract drift detected: {len(drifts)} endpoints",
                confidence=0.95,
                evidence=[Evidence(type="contract", ref=ctx.design.api_contract)],
            )

        return drifts
```

---

## Phase 4: Operations Enhancements

### 4.1 Intelligent Incident Context

**Metadata Used**:
- `design.adr` → Architectural decisions relevant to incident
- `risks[]` → Pre-identified risks and mitigations
- `agentInsights.lessons` → Past learnings
- `observability.runbook` → Operational procedures

**Implementation** (Alert annotation enrichment):
```python
def enrich_alert_annotations(alert: Alert, ctx: ProjectContextSpec) -> Alert:
    """Enrich alert with ProjectContext intelligence."""

    enrichments = {}

    # Add relevant ADR
    if ctx.design and ctx.design.adr:
        enrichments["architecture_decision"] = ctx.design.adr
        enrichments["adr_summary"] = fetch_adr_summary(ctx.design.adr)

    # Add relevant risks and mitigations
    relevant_risks = [r for r in ctx.risks if r.type.value in alert.labels.get("category", "")]
    if relevant_risks:
        enrichments["known_risks"] = [
            f"{r.description} - Mitigation: {r.mitigation}"
            for r in relevant_risks
        ]

    # Add past lessons
    querier = InsightQuerier()
    lessons = querier.get_lessons(
        project_id=ctx.project.id,
        category=alert.labels.get("alertname", "").lower(),
    )
    if lessons:
        enrichments["past_lessons"] = [l.summary for l in lessons[:3]]

    # Add runbook
    if ctx.observability and ctx.observability.runbook:
        enrichments["runbook"] = str(ctx.observability.runbook)

    # Add business context for prioritization
    if ctx.business:
        enrichments["business_criticality"] = ctx.business.criticality.value
        enrichments["business_value"] = ctx.business.value.value
        enrichments["owner"] = ctx.business.owner

    alert.annotations.update(enrichments)
    return alert
```

**Benefit**: On-call engineers see architectural context, known risks, past learnings, and runbooks directly in alert.

---

### 4.2 Predictive Capacity Alerting

**Metadata Used**:
- `requirements.throughput` → Expected traffic
- `requirements.availability` → Required uptime
- Historical metrics + `agentInsights` → Trend analysis

**Implementation**:
```python
def generate_capacity_alerts(ctx: ProjectContextSpec) -> List[PrometheusRule]:
    """Generate predictive capacity alerts from requirements."""

    rules = []

    if req := ctx.requirements:
        if req.throughput:
            target_rps = parse_throughput(req.throughput)

            # Alert when approaching capacity
            rules.append(PrometheusRule(
                alert=f"{ctx.project.id}CapacityWarning",
                expr=f'''
                    (
                        rate(http_requests_total{{service="{ctx.project.id}"}}[5m])
                        / {target_rps}
                    ) > 0.8
                ''',
                for_duration="5m",
                labels={
                    "severity": "warning",
                    "contextcore_managed": "true",
                },
                annotations={
                    "summary": f"Service approaching capacity limit ({target_rps} rps)",
                    "description": "Current traffic is >80% of designed throughput",
                    "derived_from": "requirements.throughput",
                },
            ))

            # Predict breach using linear regression
            rules.append(PrometheusRule(
                alert=f"{ctx.project.id}CapacityPrediction",
                expr=f'''
                    predict_linear(
                        rate(http_requests_total{{service="{ctx.project.id}"}}[1h])[6h:1m],
                        3600
                    ) > {target_rps}
                ''',
                for_duration="15m",
                labels={
                    "severity": "warning",
                    "type": "predictive",
                },
                annotations={
                    "summary": f"Predicted capacity breach in ~1 hour",
                    "description": "Linear projection suggests throughput will exceed design capacity",
                },
            ))

    return rules
```

---

### 4.3 Automated Runbook Generation

**Metadata Used**:
- `risks[]` → Failure scenarios and mitigations
- `targets[]` → Resources to check/restart
- `design.adr` → Architectural context
- `agentInsights.decisions` → Past decisions

**Implementation**:
```python
def generate_runbook(ctx: ProjectContextSpec) -> Runbook:
    """Generate operational runbook from ProjectContext."""

    runbook = Runbook(
        title=f"{ctx.project.id} Operational Runbook",
        generated_from="ProjectContext",
    )

    # Service overview
    runbook.add_section(Section(
        title="Service Overview",
        content=f"""
**Project**: {ctx.project.id}
**Epic**: {ctx.project.epic or 'N/A'}
**Owner**: {ctx.business.owner if ctx.business else 'N/A'}
**Criticality**: {ctx.business.criticality.value if ctx.business else 'N/A'}
**Business Value**: {ctx.business.value.value if ctx.business else 'N/A'}
        """.strip()
    ))

    # SLOs
    if req := ctx.requirements:
        runbook.add_section(Section(
            title="Service Level Objectives",
            content=f"""
| Metric | Target | Source |
|--------|--------|--------|
| Availability | {req.availability or 'N/A'}% | requirements.availability |
| Latency P50 | {req.latency_p50 or 'N/A'} | requirements.latency_p50 |
| Latency P99 | {req.latency_p99 or 'N/A'} | requirements.latency_p99 |
| Error Budget | {req.error_budget or 'N/A'}% | requirements.errorBudget |
| Throughput | {req.throughput or 'N/A'} | requirements.throughput |
            """.strip()
        ))

    # Known risks and mitigations
    if ctx.risks:
        risks_content = "| Risk | Priority | Mitigation |\n|------|----------|------------|\n"
        for risk in ctx.risks:
            risks_content += f"| {risk.description} | {risk.priority.value if risk.priority else 'N/A'} | {risk.mitigation or 'N/A'} |\n"

        runbook.add_section(Section(
            title="Known Risks & Mitigations",
            content=risks_content
        ))

    # Resources
    if ctx.targets:
        resources_content = "```bash\n"
        for target in ctx.targets:
            ns = target.namespace or "default"
            resources_content += f"kubectl get {target.kind.lower()} {target.name} -n {ns}\n"
        resources_content += "```"

        runbook.add_section(Section(
            title="Kubernetes Resources",
            content=resources_content
        ))

    # Common procedures
    runbook.add_section(Section(
        title="Common Procedures",
        content=generate_common_procedures(ctx)
    ))

    return runbook

def generate_common_procedures(ctx: ProjectContextSpec) -> str:
    """Generate common operational procedures."""

    procedures = []

    # Restart procedure
    if ctx.targets:
        target = ctx.targets[0]
        ns = target.namespace or "default"
        procedures.append(f"""
### Restart Service

```bash
kubectl rollout restart {target.kind.lower()}/{target.name} -n {ns}
kubectl rollout status {target.kind.lower()}/{target.name} -n {ns}
```
        """)

    # Scale procedure (for critical services)
    if ctx.business and ctx.business.criticality in [Criticality.CRITICAL, Criticality.HIGH]:
        procedures.append("""
### Emergency Scale Up

```bash
kubectl scale deployment/{name} --replicas=5 -n {ns}
```

**Note**: Remember to scale back down after incident resolution.
        """)

    # Log investigation
    procedures.append(f"""
### Log Investigation

```bash
# Loki query for errors
{{job="{ctx.project.id}"}} |= "error" | json

# Recent logs
kubectl logs -l app={ctx.project.id} --tail=100 -n {ns}
```
    """)

    return "\n".join(procedures)
```

---

## Phase 5: Cross-Cutting Intelligence

### 5.1 Knowledge Graph Construction

**Concept**: Build a queryable graph of service dependencies, ownership, and impact from ProjectContext relationships.

```python
class ProjectContextGraph:
    """Build knowledge graph from ProjectContext relationships."""

    def build(self, contexts: List[ProjectContext]) -> Graph:
        graph = Graph()

        for ctx in contexts:
            # Add project node
            project_node = graph.add_node(
                id=ctx.spec.project.id,
                type="project",
                attributes={
                    "criticality": ctx.spec.business.criticality if ctx.spec.business else None,
                    "value": ctx.spec.business.value if ctx.spec.business else None,
                    "owner": ctx.spec.business.owner if ctx.spec.business else None,
                }
            )

            # Add target nodes and edges
            for target in ctx.spec.targets:
                target_id = f"{target.namespace or 'default'}/{target.kind}/{target.name}"
                target_node = graph.add_node(
                    id=target_id,
                    type="k8s_resource",
                    attributes={"kind": target.kind}
                )
                graph.add_edge(project_node, target_node, relationship="manages")

            # Add design artifact nodes
            if ctx.spec.design:
                if ctx.spec.design.adr:
                    adr_node = graph.add_node(id=ctx.spec.design.adr, type="adr")
                    graph.add_edge(project_node, adr_node, relationship="implements")

                if ctx.spec.design.api_contract:
                    contract_node = graph.add_node(id=str(ctx.spec.design.api_contract), type="contract")
                    graph.add_edge(project_node, contract_node, relationship="exposes")

        return graph

    def impact_analysis(self, graph: Graph, changed_project: str) -> ImpactReport:
        """Analyze impact of changes to a project."""

        # Find all downstream dependencies
        downstream = graph.traverse(
            start=changed_project,
            direction="outgoing",
            max_depth=3
        )

        # Find all upstream dependents
        upstream = graph.traverse(
            start=changed_project,
            direction="incoming",
            max_depth=3
        )

        # Calculate blast radius
        affected_projects = set()
        for node in downstream + upstream:
            if node.type == "project":
                affected_projects.add(node.id)

        # Prioritize by criticality
        critical_affected = [
            p for p in affected_projects
            if graph.get_node(p).attributes.get("criticality") == "critical"
        ]

        return ImpactReport(
            changed_project=changed_project,
            affected_projects=list(affected_projects),
            critical_projects=critical_affected,
            blast_radius=len(affected_projects),
        )
```

---

### 5.2 Agent Learning Loop

**Concept**: Agents store lessons, future agents (and humans) query them.

```python
class LearningLoop:
    """
    Continuous improvement through agent insight accumulation.

    Pattern:
    1. Agent encounters problem
    2. Agent solves problem
    3. Agent emits lesson insight
    4. Future agent queries lessons before attempting similar work
    5. Future agent applies lessons, avoiding past mistakes
    """

    def before_task(self, project_id: str, task_type: str) -> List[Lesson]:
        """Query relevant lessons before starting work."""
        querier = InsightQuerier()

        lessons = querier.get_lessons(
            project_id=project_id,
            category=task_type,
            min_confidence=0.7,
        )

        # Also check global lessons (cross-project)
        global_lessons = querier.get_lessons(
            project_id="*",
            category=task_type,
            min_confidence=0.9,  # Higher bar for global
        )

        return lessons + global_lessons

    def after_task(self, project_id: str, task_result: TaskResult):
        """Emit lessons learned from completed task."""
        emitter = InsightEmitter(project_id=project_id)

        if task_result.had_blockers:
            for blocker in task_result.blockers:
                emitter.emit_lesson(
                    summary=f"Blocker encountered: {blocker.summary}",
                    category=task_result.task_type,
                    applies_to=task_result.affected_files,
                    resolution=blocker.resolution,
                )

        if task_result.unexpected_findings:
            for finding in task_result.unexpected_findings:
                emitter.emit_lesson(
                    summary=finding,
                    category=task_result.task_type,
                    applies_to=task_result.affected_files,
                )
```

---

## Implementation Roadmap

### Priority 1: High Value, Low Effort
1. **Alert annotation enrichment** - Add ADR, risks, runbook to alerts
2. **Cost label generation** - Auto-tag resources with business context
3. **Runbook generation** - CLI command to generate from ProjectContext

### Priority 2: High Value, Medium Effort
4. **SLO test generation** - Generate k6/chaos tests from requirements
5. **Risk-based PR review** - GitHub Action for review guidance
6. **Contract drift detection** - Continuous contract verification

### Priority 3: Strategic
7. **Knowledge graph** - Dependency and impact visualization
8. **Agent learning loop** - Cross-session knowledge accumulation
9. **IDE plugin** - Real-time ProjectContext visibility in editor

---

## Quick Prompt for Implementation

```
Implement ContextCore lifecycle integration features:

1. Add alert enrichment to operator.py - when generating PrometheusRules, include annotations for:
   - design.adr (architecture decision reference)
   - relevant risks and mitigations from risks[]
   - runbook URL from observability.runbook
   - business.criticality and business.owner

2. Create new CLI command `contextcore generate runbook` that outputs markdown runbook from ProjectContext

3. Create new CLI command `contextcore generate slo-tests` that outputs k6 load test scripts derived from requirements

4. Add cost attribution labels to all generated artifacts (ServiceMonitor, Dashboard ConfigMap) using business.costCenter and business.owner

5. Enhance the operator to emit lessons as insights when it encounters errors during artifact generation

Reference the LIFECYCLE_INTEGRATION_OPPORTUNITIES.md for detailed implementation patterns.
```
