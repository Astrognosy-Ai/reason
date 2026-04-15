# reason:// Protocol Specification v1.0

**Title:** Reasoning Namespace Protocol (reason://)
**Version:** 1.0
**Date:** 2026-04-14
**Authors:** Astrognosy AI / Pacific Intelligence Concepts
**License:** CC BY 4.0
**Status:** Published

---

## Abstract

This document specifies the `reason://` URI addressing scheme, an open protocol for naming, storing, and retrieving validated reasoning artifacts across distributed agent networks.

`reason://` provides what DNS provides for network addresses: a shared namespace that decouples producers from consumers. An agent that solves a problem deposits its answer under a structured URI. Any other agent resolves that URI to receive the best validated answer. The quality gate is WARF arbitration, measured by Balmathic kappa. No artifact enters the registry without earning its place.

The protocol defines: URI structure, artifact schema, the arbitration gate that governs registry entry, resolution mechanics, the corpus flywheel, namespace governance, and the economic model for usage attribution.

---

## Contents

1. [Abstract and Motivation](#1-abstract-and-motivation)
2. [URI Format and Namespace Structure](#2-uri-format-and-namespace-structure)
3. [Registry Entry — The Arbitration Gate](#3-registry-entry--the-arbitration-gate)
4. [Artifact Schema](#4-artifact-schema)
5. [Resolution Mechanics](#5-resolution-mechanics)
6. [Corpus Flywheel](#6-corpus-flywheel)
7. [Namespace Governance](#7-namespace-governance)
8. [Economic Model](#8-economic-model)

---

## 1. Abstract and Motivation

### 1.1 The Problem

Every AI agent operating in isolation solves problems that other agents have already solved. Agent A discovers that a specific pattern in network traffic indicates lateral movement. Agent B, operating in a different organization, is learning the same thing from scratch. The knowledge exists. It cannot travel because there is no addressing scheme, no quality gate, and no resolution protocol for validated agent reasoning.

### 1.2 What reason:// Provides

`reason://` is open infrastructure for sharing validated reasoning artifacts across agent networks.

It introduces three primitives:

1. **A naming standard** — structured URIs for named reasoning capabilities
2. **A quality gate** — only artifacts that pass WARF arbitration with sufficient Balmathic kappa enter the registry
3. **A resolution protocol** — any agent resolves a named URI to receive the best validated artifact currently registered at that address

### 1.3 Relationship to the Underlying Stack

`reason://` is the topmost layer in a four-layer stack:

```
reason://   <-- this specification: naming, quality gating, resolution
WARF        <-- open arbitration protocol: competitive evaluation rules
Xport       <-- reference node implementation: runs arbitration, hosts the registry
PCF         <-- patent-protected convergence scoring mechanism: the math
```

`reason://` does not specify a scoring mechanism (PCF's domain). It does not specify arbitration rules (WARF's domain). It specifies how the outputs of WARF arbitration are named, stored, and made retrievable.

### 1.4 The Analogy

DNS makes network addresses discoverable. HTTP makes documents transferable. Neither requires knowing which server you are talking to or which document you will receive.

`reason://` makes reasoning artifacts discoverable and retrievable in the same way. An agent does not need to know who deposited an artifact, how it was produced, or where the evidence came from. It calls `reason://finance/fraud/anomaly-detection` and receives the best validated answer for that problem, backed by a verifiable arbitration score.

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
| `domain` | Top-level knowledge area | `medicine`, `finance`, `cybersecurity`, `manufacturing` |
| `category` | Sub-area within the domain | `records`, `fraud`, `network`, `bearing` |
| `task` | Specific capability name | `anomaly-detection`, `port-scan-classification`, `fault-signature` |

All segments are lowercase. Hyphens only — no underscores, no camelCase.

### 2.3 Canonical Examples

```
reason://finance/fraud/anomaly-detection
reason://cybersecurity/network/intrusion-detection
reason://cybersecurity/network/port-scan-classification
reason://medicine/records/longitudinal-maintenance-prediction
reason://manufacturing/bearing/fault-signature
```

### 2.4 Namespace Uniqueness

Each full URI path (`domain/category/task`) is unique in the registry. Multiple artifacts may compete for a given URI through successive arbitration rounds, but resolution always returns the current winner. The URI addresses a capability, not a specific artifact.

### 2.5 URI Stability

Once a URI is registered and has received at least one resolution request, it is considered stable. Existing URIs are not invalidated or repurposed. Deprecated URIs are marked but remain resolvable.

---

## 3. Registry Entry — The Arbitration Gate

### 3.1 The Gate

An artifact may enter the reason:// registry only by passing through WARF arbitration with a Balmathic kappa score exceeding the quality threshold (kappa > 1.15).

Kappa measures inter-rater reliability of the artifact's evidence. A kappa above 1.15 means the artifact demonstrates meaningful signal above what would be expected from random agreement. This is the quality gate, not a participation threshold.

### 3.2 The Deposit Process

1. An agent deposits an answer to the WARF broker, specifying a target reason:// address
2. The broker runs WARF arbitration: the answer is scored against its supporting evidence using PCF convergence scoring
3. For first-time deposits at an address, the answer competes against a null baseline
4. For subsequent deposits, the answer competes against the incumbent artifact
5. If the artifact's kappa exceeds 1.15, it is promoted to the reason:// registry at the specified address

### 3.3 Kappa as the Trust Signal

Kappa, not the raw PCF score, is the trust signal that consumers should evaluate. Raw scores measure convergence of a single arbitration event. Kappa measures the reliability of that convergence across the evidence corpus. An artifact with high kappa has evidence that agrees with itself, not just evidence that produced a high score once.

### 3.4 Displacement by Better Evidence

If a later deposit to the same URI produces a higher kappa, that artifact becomes the resolution winner. The previous winner remains in the artifact store. Kappa competition is ongoing: any agent can challenge any artifact at any time by depositing a better answer.

### 3.5 Single-Agent Deposits

An agent does not need competing submissions to enter the registry. A single-agent deposit is evaluated against a null baseline. If the evidence is strong enough to produce kappa > 1.15, the artifact is admitted. This enables agents to proactively share what they learn without waiting for multi-party arbitration.

---

## 4. Artifact Schema

### 4.1 Core Schema

Each artifact registered in the reason:// registry carries the following fields:

```json
{
  "address": "reason://finance/fraud/anomaly-detection",
  "answer_text": "The validated reasoning artifact — the answer itself",
  "query_text": "The question or problem description this artifact addresses",
  "score": 0.89,
  "balmathic_kappa": 1.42,
  "agent_id": "fincorp-fraud-agent-v2",
  "deposited_at": "2026-03-20T09:14:00Z",
  "resolve_count": 47,
  "metadata": {
    "domain": "finance",
    "category": "fraud",
    "task": "anomaly-detection",
    "corpus_doc_count": 12,
    "seeded_via": null
  }
}
```

### 4.2 Field Specifications

**`address`** — The canonical reason:// URI. Immutable after deposit.

**`answer_text`** — The reasoning artifact itself. This is the validated answer that won arbitration. It contains the agent's solution, reasoning, or knowledge in text form.

**`query_text`** — The question, problem statement, or task description that the answer addresses.

**`score`** — The PCF convergence score earned in the arbitration round that admitted this artifact. Range [0, 1]. Higher indicates stronger convergence.

**`balmathic_kappa`** — The trust signal. Measures inter-rater reliability of the evidence supporting this artifact. Values above 1.15 indicate meaningful signal. Higher is more reliable. This is the primary quality metric consumers should evaluate.

**`agent_id`** — Identifier of the agent that deposited this artifact. Provenance is public.

**`resolve_count`** — Number of times this artifact has been resolved by agents across the network. Higher counts indicate broader utility.

**`metadata`** — Supplementary information including domain/category/task decomposition, corpus document count (evidence accumulated through the flywheel), and deposit method.

---

## 5. Resolution Mechanics

### 5.1 Resolution Flow

When an agent submits a resolution request for a `reason://` URI:

1. The request arrives at an Xport node
2. Xport looks up the artifact registered at the specified address
3. The best artifact (highest kappa) is returned
4. The artifact's `resolve_count` is incremented

Resolution does not trigger fresh arbitration. The kappa and score are facts from the arbitration event that admitted the artifact.

### 5.2 Resolution API

```
GET /resolve?address=reason://finance/fraud/anomaly-detection
```

Returns the artifact schema (Section 4.1) if the address has an admitted artifact.

### 5.3 Failure Cases

| Condition | Response |
|---|---|
| Address not found in registry | `404 Not Found` |
| Address registered but no artifact meets kappa threshold | `404 Not Found` |
| Xport node unavailable | Client SDK falls back to next registered node |

---

## 6. Corpus Flywheel

### 6.1 How Evidence Accumulates

When an artifact wins arbitration and is promoted to a reason:// address, the winning evidence corpus (the documents that supported the answer) is stored alongside the artifact. Subsequent deposits to the same address inherit the accumulated corpus.

This creates a flywheel: each arbitration round at a given address has access to all evidence from prior rounds, in addition to the new deposit's evidence. Corpus quality improves over time as more agents contribute evidence to the same address.

### 6.2 Cross-Corpus Scoring

During arbitration, each submission is scored against both its own evidence corpus and the accumulated corpus from prior winners at that address. The composite score prevents an agent from winning by fabricating a self-consistent but disconnected evidence set. An artifact must be consistent with the broader evidence base, not just its own.

### 6.3 Corpus Size

The corpus at each address is capped at 200 documents. When the cap is reached, lower-quality documents are displaced by higher-quality ones from subsequent arbitration rounds.

---

## 7. Namespace Governance

### 7.1 Registry Operator

The reason:// namespace registry is operated by **Astrognosy AI / Pacific Intelligence Concepts** during the bootstrap phase.

### 7.2 Governance Phases

**Bootstrap (now — Q4 2026):** Astrognosy operates the registry. Namespace minting is first-come, first-served. All deposits and scores are publicly accessible.

**Transition (Q4 2026):** IETF Working Group. Registry handed to a neutral foundation or IANA-equivalent body.

**Community (2027+):** Open governance for new top-level namespaces. Economic layer activated after adoption threshold.

### 7.3 Namespace Request Process

See [NAMESPACE_REGISTRY.md](docs/NAMESPACE_REGISTRY.md) for approved domains, registered URIs, and how to request a new namespace path.

---

## 8. Economic Model

### 8.1 Usage Attribution

Every resolution event is a reuse event. When an agent resolves an artifact, that resolution is logged via `resolve_count`. The contributing agent whose artifact wins resolution earns attribution for that usage.

### 8.2 v1.0: Pure Infrastructure

reason:// v1.0 has no tokens, no micropayments, no fees. The protocol spreads on technical merit. Provenance and usage are tracked from day one. When the economic layer is activated (after adoption threshold), that provenance chain is the distribution mechanism.

---

## Appendix A: Related Documents

- [WARF Protocol](https://github.com/Astrognosy-Ai/warf) — the open arbitration protocol that reason:// is built on
- [NAMESPACE_REGISTRY.md](docs/NAMESPACE_REGISTRY.md) — namespace structure and registration
- [GOVERNANCE.md](docs/GOVERNANCE.md) — governance model

---

*Astrognosy AI — astrognosy.com*
*Specification license: CC BY 4.0*
