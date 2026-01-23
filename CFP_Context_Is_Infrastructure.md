
# Conference Proposal (CFP)
## Title
**Context Is Infrastructure: Why Alerts Without Context Fail in Kubernetes**

## Abstract
Modern observability tells us *what* is broken, but rarely *why it matters*. In large Kubernetes environments, on-call engineers are flooded with alerts that lack business meaning, ownership clarity, and design intent. This talk introduces **Context-Aware Observability** — a practical approach that treats context (ownership, criticality, risk, and design intent) as first-class infrastructure.

Using real-world patterns and live demos, we will show how embedding context directly into Kubernetes using Custom Resource Definitions (CRDs) enables faster incident response, clearer prioritization, and lower cognitive load for SRE and platform teams.

Attendees will leave with concrete techniques they can apply immediately, whether or not they adopt ContextCore.

## Talk Type
Technical / Practitioner Talk

## Audience
- SREs
- Platform Engineers
- DevOps Engineers
- Cloud-Native Architects

## Level
Intermediate

## Key Takeaways
- Why alerts without context increase MTTR
- How Kubernetes-native context changes incident response
- Practical patterns for enriching telemetry with business meaning
- How to avoid CMDB rot in dynamic environments

## Outline
1. The Observability Gap (10 min)
2. Why CMDBs and Service Catalogs Fail at Runtime (10 min)
3. Context as Infrastructure (10 min)
4. Live Demo: Context-Enriched Alerts in Kubernetes (15 min)
5. Lessons Learned & Adoption Patterns (10 min)
6. Q&A (5 min)

## Speaker Bio
Platform engineer and systems thinker focused on reliability, observability, and scalable operations in Kubernetes-heavy environments. Builder of ContextCore.

## Why This Talk Fits KubeCon / SREcon
This talk aligns directly with cloud-native operational challenges faced by modern SRE teams and advances the community conversation around observability beyond metrics and traces toward semantic understanding.
