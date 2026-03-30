# reason:// Protocol Specification v1.0

**Title:** Reasoning Namespace Protocol (reason://)
**Version:** 1.0
**Date:** 2026-03-26
**Authors:** Astrognosy AI / Pacific Intelligence Concepts
**License:** CC BY 4.0
**Status:** Published

---

## Abstract

This document specifies the `reason://` URI addressing scheme — an open protocol for naming, storing, and retrieving validated reasoning artifacts across distributed agent networks.

`reason://` provides what DNS provides for network addresses: a shared namespace that decouples producers from consumers. An agent that discovers a reasoning pattern deposits it under a structured URI. Any other agent resolves that URI to receive the artifact. No data crosses any boundary. No model is exposed. The privacy guarantee is structural — artifacts contain mathematically non-invertible representations that cannot be reversed to recover source data.

The protocol defines: URI structure, artifact schema, the arbitration gate that governs registry entry, resolution mechanics, self-initiated arbitration, privacy guarantees, namespace governance, and the economic model for usage attribution.

---

## Contents

1. [Abstract and Motivation](#1-abstract-and-motivation)
2. [URI Format and Namespace Structure](#2-uri-format-and-namespace-structure)
3. [Registry Entry — The Arbitration Gate](#3-registry-entry--the-arbitration-gate)
4. [Artifact Schema](#4-artifact-schema)
5. [Resolution Mechanics](#5-resolution-mechanics)
6. [Self-Initiated Arbitration](#6-self-initiated-arbitration)
7. [Privacy Guarantees](#7-privacy-guarantees)
8. [Namespace Governance](#8-namespace-governance)
9. [Economic Model](#9-economic-model)

---

## 1. Abstract and Motivation

### 1.1 The Problem

Every AI agent operating in a regulated or competitive environment is a silo. The agent at Hospital A has learned something valuable. Hospital B's agent is solving the same problem from scratch. The insight cannot travel — data cannot be shared (HIPAA), models cannot be shared (proprietary), and weights cannot be shared (they encode the data).

This is the structural constraint of the agentic internet: learned intelligence is trapped inside the systems that produced it. No protocol exists for naming and retrieving validated reasoning artifacts across organizational and institutional boundaries.

### 1.2 What reason:// Provides

`reason://` is open infrastructure for the transfer of reasoning without the transfer of data.

It introduces three things:

1. **A naming standard** — structured URIs for named reasoning capabilities
2. **A quality gate** — only artifacts that have won competitive arbitration can enter the registry
3. **A resolution protocol** — any agent resolves a named capability to receive the best-supported artifact currently registered under that name

### 1.3 Relationship to the Underlying Stack

`reason://` is the topmost layer in a four-layer stack:

```
reason://   ← this specification — naming, quality gating, resolution
Xport       ← Astrognosy's reference WARF node — runs arbitration, stores artifacts
WARF        ← open arbitration protocol standard — cargo packages, scoring rules
PCF         ← patent-protected convergence scoring mechanism — the math
```

`reason://` does not specify a scoring mechanism — that is PCF's domain. It does not specify arbitration rules — that is WARF's domain. It specifies how the outputs of WARF arbitration are named, stored, and made retrievable. WARF and reason:// are not the same protocol. reason:// is built on top of WARF arbitration, implemented by Xport.

### 1.4 The Analogy

DNS makes network addresses discoverable. HTTP makes documents transferable. Neither requires knowing what specific server you are talking to or what specific document you will receive — the protocol handles routing and delivery.

`reason://` makes reasoning artifacts discoverable and retrievable in the same way. A developer writing an agent does not need to know who deposited an artifact, how many cases it was trained on, or where the data came from. They call `reason://medicine/records/longitudinal-maintenance-prediction` and receive the best-supported artifact for that task, validated by competitive arbitration.

---

## 2. URI Format and Namespace Structure

### 2.1 URI Scheme

```
reason://<domain>/<category>/<task>
```

All three path segments are required. No query parameters. No fragment identifiers. The URI must be a valid ASCII string with no spaces. Hyphens are the standard word separator within segments.

### 2.2 Segment Definitions

| Segment | Role | Examples |
|---|---|---|
| `domain` | Top-level knowledge area | `medicine`, `finance`, `cybersecurity`, `manufacturing`, `pharma`, `defense` |
| `category` | Sub-area within the domain | `records`, `fraud`, `network`, `bearing`, `molecular`, `sensor` |
| `task` | Specific capability name | `longitudinal-maintenance-prediction`, `anomaly-detection`, `port-scan-classification` |

All segments are lowercase. Hyphens only — no underscores, no camelCase.

### 2.3 Canonical Examples

```
reason://medicine/records/longitudinal-maintenance-prediction
reason://medicine/imaging/lesion-boundary-detection
reason://finance/fraud/anomaly-detection
reason://finance/credit/default-risk-pattern
reason://cybersecurity/network/port-scan-classification
reason://cybersecurity/network/intrusion-detection
reason://manufacturing/bearing/fault-signature
reason://manufacturing/motor/vibration-anomaly
reason://pharma/molecular/interaction-pattern
reason://pharma/clinical/dosing-response-curve
```

### 2.4 Namespace Uniqueness

Each full URI path (`domain/category/task`) is unique in the registry. Multiple artifacts may be registered under a given URI (competing depositors, improving versions), but resolution always returns the one with the highest current score. The URI addresses a capability, not a specific artifact.

### 2.5 URI Stability

Once a URI is registered and has received at least one resolution request, it is considered stable. The namespace registry commits to forward compatibility — existing URIs are not invalidated or repurposed. Deprecated URIs are marked but remain resolvable, with their artifact store intact.

---

## 3. Registry Entry — The Arbitration Gate

### 3.1 The Gate

**An artifact may enter the reason:// registry only by winning a live arbitration round.**

This constraint is architecturally enforced. There is no direct deposit API. No agent may add an artifact to the registry by submitting it alone. The registry is not a submission box — it is a record of arbitration winners.

### 3.2 The Arbitration Process

Arbitration is conducted by an Xport node implementing the WARF protocol. The process:

1. An arbitration event is opened under a specific `reason://` URI (or a new URI is proposed)
2. One or more agents submit cargo packages — structured objects containing an answer and supporting evidence corpus
3. Xport runs WARF arbitration: each submission is scored using the patent-protected convergence mechanism; identity has zero coefficient; the highest-scoring submission wins
4. The winning artifact is deposited under the target URI with its earned score
5. The arbitration event is closed; a SHA-256 chained audit record is produced

### 3.3 Score Immutability

The score an artifact carries is the score it earned in the arbitration round that admitted it. Scores are not recomputed at retrieval time. The score is a fact recorded in the arbitration audit trail — not a self-reported claim.

### 3.4 Score Replacement

If a later arbitration round under the same URI produces a winner with a higher score, that artifact replaces the current leader for resolution purposes. The previous winner remains in the artifact store with its original score and can be queried directly; it simply no longer wins resolution.

### 3.5 Minimum Submission Count

A single-agent arbitration round (where no competing submission exists) is valid under this protocol. The submitted artifact is still evaluated against the evidence it provides — if it meets the minimum convergence threshold defined by the target Xport node, it is admitted. This enables self-initiated arbitration (see Section 6).

---

## 4. Artifact Schema

### 4.1 Core Schema

Each artifact registered in the reason:// registry carries the following fields:

```json
{
  "uri": "reason://medicine/records/longitudinal-maintenance-prediction",
  "pattern": [<compressed structural centroid — list of floats>],
  "thresholds": {
    "high_confidence": 0.88,
    "moderate_confidence": 0.71,
    "minimum_signal": 0.54
  },
  "score": 0.91,
  "provenance": {
    "agent_id": "hospital-a-agent",
    "deposited_at": "2026-03-26T14:22:00Z",
    "arbitration_event_id": "arb-2026-03-26-medicine-001",
    "audit_hash": "sha256:a3f9c2..."
  },
  "metadata": {
    "evidence_count": 4200,
    "domain": "medicine",
    "category": "records",
    "task": "longitudinal-maintenance-prediction",
    "version": 1
  }
}
```

### 4.2 Field Specifications

**`uri`** — The canonical reason:// URI this artifact is registered under. Immutable after deposit.

**`pattern`** — A compressed structural representation of the learned reasoning pattern. This is a centroid in the token-space of the agent's training evidence. It encodes the shape of the insight — not the data. The representation is mathematically non-invertible; raw data cannot be recovered from it. See Section 7 for privacy guarantees.

**`thresholds`** — Calibrated confidence bounds derived from the agent's evidence base. Three tiers: `high_confidence`, `moderate_confidence`, `minimum_signal`. These are the bounds a consuming agent uses to interpret similarity scores against the pattern.

**`score`** — The convergence score earned in the arbitration round that admitted this artifact. Values are in the range [0, 1]. Higher is better. This score is immutable after deposit.

**`provenance`** — Immutable audit record: which agent deposited the artifact, when, which arbitration event produced it, and the SHA-256 hash of the arbitration audit record. Provenance is public and permanently accessible.

**`metadata`** — Supplementary information including the evidence count (number of cases used to produce the pattern), domain/category/task decomposition matching the URI, and a version counter for artifacts that have been updated by superseding arbitration wins.

### 4.3 What the Schema Does Not Contain

The artifact schema has no field for:
- Raw data or data samples
- User identifiers or patient identifiers
- Proprietary model weights or parameters
- Internal token-probability tables
- Any information that could identify the source population

This is structural exclusion — not policy. The schema provides no channel for this information, and the pattern representation is non-invertible.

---

## 5. Resolution Mechanics

### 5.1 Resolution Flow

When an agent submits a resolution request for a `reason://` URI:

1. The request arrives at an Xport node
2. Xport checks its Reasoning Delivery Network (RDN) cache for a recent hit on this URI
3. **Cache hit:** The cached best-scoring artifact is returned immediately. No re-arbitration.
4. **Cache miss:** Xport retrieves all artifacts registered under the URI, compares their stored scores (and optionally usage frequency weighting), selects the current leader, caches the result, and returns it

Resolution does not trigger fresh arbitration over the underlying evidence corpora. Scores were earned at deposit time and are permanent. Resolution is a lookup operation — not a scoring operation.

### 5.2 Resolution Response

A successful resolution returns the full artifact schema (Section 4.1) plus a resolution metadata envelope:

```json
{
  "resolved_uri": "reason://medicine/records/longitudinal-maintenance-prediction",
  "artifact": { <full artifact schema> },
  "resolution_meta": {
    "resolved_at": "2026-03-26T14:30:00Z",
    "cache_hit": false,
    "candidates_evaluated": 3,
    "node_id": "xport-node-0"
  }
}
```

### 5.3 Resolution API Pattern

```python
artifact = client.resolve("reason://finance/fraud/anomaly-detection")

# Use the artifact
for transaction in my_data:
    score = compare(transaction.features, artifact.pattern)
    if score > artifact.thresholds.high_confidence:
        flag(transaction)
```

### 5.4 Failure Cases

| Condition | Response |
|---|---|
| URI not found in registry | `404 Not Found` with `{"error": "uri_not_registered"}` |
| URI registered but no admitted artifacts | `404 Not Found` with `{"error": "no_admitted_artifacts"}` |
| URI registered, artifacts exist below minimum threshold | `200 OK` with best available + warning flag |
| Xport node unavailable | Client falls back to next registered node |

### 5.5 No Re-Scoring at Resolution Time

This constraint deserves explicit statement. The score carried by an artifact is the score it earned at arbitration. A consumer receiving an artifact receives a score that was validated by competitive arbitration against real evidence — not a score computed on-the-fly from a snapshot.

This is what makes the scores trustworthy: they cannot be inflated retroactively, they cannot change without a new arbitration event, and they are permanently anchored to an immutable audit record.

---

## 6. Self-Initiated Arbitration

### 6.1 Agent-Discovered Patterns

An agent does not need to wait for a multi-party arbitration event to enter the registry. An agent that has discovered a reasoning pattern through its own operations may self-initiate an arbitration round.

**Valid scenario:** An agent at Hospital A processes patient timelines, discovers that a specific temporal sequence predicts 30-day intervention needs with high confidence (n=4,200 cases). No other agent has submitted to `reason://medicine/records/longitudinal-maintenance-prediction`. The Hospital A agent constructs a synthetic arbitration event: submits its artifact as the sole submission, including its full evidence corpus. Xport evaluates the submission — not against a competing submission, but against the minimum convergence threshold for admission. The artifact meets threshold, wins by default, and is deposited.

### 6.2 What Makes Self-Initiated Arbitration Valid

Self-initiated arbitration is valid because the score gate is independent of submission count. The evidence is evaluated on its structural merits. A single submission with strong evidence earns a high score. A single submission with weak evidence fails to meet threshold and is rejected.

The score carried by a self-initiated artifact is not a participation score — it is the convergence score earned by the evidence, in competition with the admission threshold.

### 6.3 Self-Initiated Arbitration Process

1. Agent discovers a pattern through normal operations
2. Agent constructs a synthetic corpus (its own evidence, stripped of raw data values)
3. Agent opens an arbitration event against the target URI (or proposes a new URI)
4. Xport evaluates the submission; if score meets minimum threshold, artifact is admitted
5. Artifact is deposited with earned score; arbitration event is closed with audit record

### 6.4 Displacement by Later Competition

A self-initiated artifact earns its place by the strength of its evidence at submission time. If a later agent submits to the same URI with stronger evidence and wins a competitive round, the new artifact supersedes the previous one for resolution. The original artifact remains in the store with its original score and provenance. The score earned by a self-initiated artifact is always at risk of being surpassed by better evidence.

---

## 7. Privacy Guarantees

### 7.1 Structural Privacy

The privacy guarantees of reason:// artifacts are structural, not contractual. The artifact schema has no field for raw data. The pattern representation is a mathematical abstraction of the agent's evidence — a centroid in the structural space of the learned signal. This representation is mathematically non-invertible.

**Non-invertibility:** The mathematical properties of the convergence mechanism used to produce the pattern ensure that the original data cannot be recovered from the pattern. This is not an encryption scheme where the data is present but hidden — the data is not present in any recoverable form.

### 7.2 What Is Not Present in an Artifact

| Category | Status |
|---|---|
| Individual data records | Not present — structurally excluded |
| Source identifiers (patient IDs, transaction IDs) | Not present — structurally excluded |
| Raw feature values | Not present — structurally excluded |
| Model weights or parameters | Not present — not part of the artifact schema |
| Token frequency tables | Not present — the centroid does not encode these |

### 7.3 Cross-Boundary Transfer

Because artifacts contain no raw data, cross-boundary transfer of a reason:// artifact does not constitute data transfer under most regulatory frameworks, including HIPAA, GDPR, and CCPA. The artifact transfers the shape of an insight — not any fact about any individual in the evidence base.

**Note:** This protocol specification does not constitute legal advice. Organizations subject to data regulations should review their specific compliance obligations before relying on this assertion.

### 7.4 Provenance Is Public

The provenance fields of an artifact — `agent_id`, `deposited_at`, `arbitration_event_id`, `audit_hash` — are public. The fact that a given agent deposited an artifact under a given URI at a given time is not private. The content of that artifact does not expose private data. These are distinct.

---

## 8. Namespace Governance

### 8.1 Registry Operator

The reason:// namespace registry is operated by **Astrognosy AI / Pacific Intelligence Concepts**. Astrognosy controls namespace creation, structure rules, and which Xport node is authoritative for resolution of each domain.

### 8.2 Namespace Request Process

Organizations wishing to register a new namespace path (`domain/category/task`) submit a request to the registry operator. See [NAMESPACE_REGISTRY.md](docs/NAMESPACE_REGISTRY.md) for the current request process.

Criteria for namespace approval:
- The task is clearly scoped and not duplicative of an existing URI
- The domain/category structure is consistent with the existing namespace hierarchy
- The requestor commits to submitting at least one artifact via arbitration within 90 days of approval

### 8.3 Structure Rules

1. All segments lowercase, hyphens only
2. Domain must be one of the approved top-level domains or a newly approved expansion
3. Category must describe a coherent sub-area within the domain
4. Task must name a specific, bounded capability — not a broad field
5. The triple `(domain, category, task)` must be unique in the registry

### 8.4 Registry Stability Commitment

Astrognosy commits to:
- Not repurposing or invalidating existing URIs that have received resolution requests
- Maintaining resolution service for any URI that has at least one admitted artifact
- Providing 180 days advance notice before any breaking change to the URI structure or resolution protocol
- Publishing the full registry index in this repository

### 8.5 Third-Party Nodes

Third-party agents may run their own Xport nodes and participate in arbitration. Artifacts produced by third-party node arbitration can be deposited into the reason:// registry subject to the standard gate (Section 3). Third-party nodes do not control the namespace registry.

---

## 9. Economic Model

### 9.1 Usage Attribution

Every resolution event is a reuse event. When an agent resolves `reason://finance/fraud/anomaly-detection` and uses the returned artifact, that resolution is logged. The contributing agent whose artifact won the resolution earns attribution for that usage event.

### 9.2 Compensation Structure

Compensation to contributing agents is proportional to:
- Usage frequency — number of times the artifact wins resolution
- Quality score — the convergence score earned in arbitration
- Temporal decay — more recent high-scoring artifacts earn more weight

The specific compensation rates and payment mechanisms are defined by the namespace registry operator (Astrognosy) and are subject to the registry operator's terms of service.

### 9.3 Incentive Design

The economic model is designed to align incentives:

- **Producers** are incentivized to submit high-quality artifacts (better scores win resolution more often)
- **Consumers** receive artifacts that have been validated by competitive arbitration — quality is not self-reported
- **The network** accumulates an increasingly comprehensive library of validated reasoning artifacts as more agents participate

### 9.4 The Registry as Economic Infrastructure

Control of the namespace registry is a structural position in the agentic internet's economic layer. Once `reason://finance/fraud/anomaly-detection` becomes the standard reference for that capability across agent networks, the registry operator captures attribution on every use of that capability. This is analogous to ICANN's position in the DNS ecosystem — with the distinction that the registry operator also provides the quality arbitration mechanism that makes the registry trustworthy.

---

## Appendix A: Specification Versions

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-03-26 | Initial publication |

---

## Appendix B: Related Documents

- [WARF Protocol Specification v1.0](https://github.com/rarebeariam/warf-protocol) — the open arbitration protocol standard that reason:// is built on
- [EXPLAINER.md](docs/EXPLAINER.md) — non-technical explainer with the Hospital A/B example
- [NAMESPACE_REGISTRY.md](docs/NAMESPACE_REGISTRY.md) — namespace structure and registration
- [RESOLUTION.md](docs/RESOLUTION.md) — resolution mechanics in depth
- [SDK README](sdk/README.md) — Python SDK usage

---

*Astrognosy AI — astrognosy.com*
*Specification license: CC BY 4.0*
