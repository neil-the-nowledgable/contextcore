#!/usr/bin/env python3
"""
UserPromptSubmit hook: Inject project context when relevant keywords detected.
Only injects context for prompts mentioning risks, SLOs, requirements, etc.
"""
import json
import sys
import os

try:
    import yaml
except ImportError:
    # yaml not available, exit silently
    sys.exit(0)

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

prompt = input_data.get("prompt", "").lower()

# Keywords that trigger context injection
context_triggers = [
    "risk",
    "requirement",
    "slo",
    "availability",
    "latency",
    "criticality",
    "owner",
    "business",
    "p1",
    "p2",
    "priority",
    "mitigation",
]

should_inject = any(trigger in prompt for trigger in context_triggers)

if not should_inject:
    sys.exit(0)

# Load and parse .contextcore.yaml
contextcore_path = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", "."), ".contextcore.yaml"
)

if not os.path.exists(contextcore_path):
    sys.exit(0)

try:
    with open(contextcore_path, "r") as f:
        context_data = yaml.safe_load(f)
except Exception:
    sys.exit(0)

# Format context for Claude
context_lines = [
    "",
    "## Relevant Project Context (auto-injected)",
    "",
]

# Project info
if "project" in context_data:
    project = context_data["project"]
    context_lines.append(f"**Project**: {project.get('id', 'unknown')} ({project.get('name', '')})")

# Business context
if "business" in context_data:
    business = context_data["business"]
    if "criticality" in business:
        context_lines.append(f"**Criticality**: {business['criticality']}")
    if "owner" in business:
        context_lines.append(f"**Owner**: {business['owner']}")

    if "risks" in business:
        context_lines.append("\n**Active Risks**:")
        for risk in business["risks"]:
            priority = risk.get("priority", "?")
            desc = risk.get("risk") or risk.get("description", "")
            mitigation = risk.get("mitigation", "None specified")
            context_lines.append(f"- [{priority}] {desc}")
            context_lines.append(f"  Mitigation: {mitigation}")

# Requirements
if "requirements" in context_data:
    context_lines.append("\n**SLO Requirements**:")
    for key, value in context_data["requirements"].items():
        context_lines.append(f"- {key}: {value}")

context_lines.append("")

# Output as JSON with additionalContext
output = {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "\n".join(context_lines),
    }
}

print(json.dumps(output))
sys.exit(0)
