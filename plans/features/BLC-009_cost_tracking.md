# Feature: BLC-009 - Add Cost Tracking Metrics

## Overview
Track and emit LLM API costs during code generation workflows.

## Target Files
- `scripts/lead_contractor/runner.py` (modify)
- `scripts/prime_contractor/workflow.py` (modify)

## Requirements

### Metrics to Track
1. **tokens_input** - Input tokens per API call
2. **tokens_output** - Output tokens per API call
3. **cost_usd** - Estimated cost in USD
4. **model_name** - Which model was used

### Implementation

#### In runner.py (Lead Contractor)
```python
from contextcore.tracing import get_tracer

tracer = get_tracer("lead-contractor")

def run_generation(self, feature):
    with tracer.start_as_current_span("code_generation") as span:
        response = self.llm_client.generate(...)

        # Record usage
        span.set_attribute("gen_ai.usage.input_tokens", response.usage.input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", response.usage.output_tokens)
        span.set_attribute("gen_ai.request.model", response.model)

        # Calculate cost (example rates)
        cost = self._calculate_cost(response.usage, response.model)
        span.set_attribute("contextcore.cost.usd", cost)
```

#### Cost Calculation
```python
COST_PER_1K_TOKENS = {
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
}

def _calculate_cost(self, usage, model):
    rates = COST_PER_1K_TOKENS.get(model, {"input": 0, "output": 0})
    return (usage.input_tokens * rates["input"] +
            usage.output_tokens * rates["output"]) / 1000
```

## Acceptance Criteria
- [ ] Token counts recorded as span attributes
- [ ] Cost calculated per generation
- [ ] Model name recorded
- [ ] Metrics visible in Grafana dashboard
- [ ] Cumulative cost per workflow run

## Dependencies
- OpenTelemetry tracer
- LLM client with usage reporting

## Size Estimate
~50 lines of code
