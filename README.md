# reason://

> **reason:// is to agent intelligence what HTTP is to information.**

An open URI addressing scheme that makes learned reasoning artifacts globally discoverable — the DNS layer for the agentic internet.

---

## The Problem

Every AI agent is a silo.

An agent at Hospital A has learned something valuable — a structural pattern that predicts patient intervention needs 30 days out, discovered across 4,200 timelines. Hospital B's agent is solving the same problem from scratch. The insight exists. It cannot move. The data is private. The model is proprietary. The weights encode the data.

This is not a healthcare problem. It is the defining constraint of distributed agent networks: **learned intelligence is trapped inside the systems that produced it.**

---

## The Solution

`reason://` is open infrastructure for sharing learned reasoning — without sharing data.

Reasoning artifacts — compressed structural representations of what an agent has learned — are addressed, stored, and retrieved via structured URIs:

```
reason://medicine/records/longitudinal-maintenance-prediction
reason://finance/fraud/anomaly-detection
reason://cybersecurity/network/port-scan-classification
reason://manufacturing/bearing/fault-detection
```

Any agent anywhere resolves that address in one line of code:

```python
from reason_py import ReasonClient

client = ReasonClient()
artifact = client.resolve("reason://finance/fraud/anomaly-detection")
```

No data shared. No model exposed. No privacy violated.

---

## How Artifacts Enter the Registry

**Artifacts enter reason:// only by winning a live arbitration round.**

The registry is not a submission box. It is a record of validated winners. When an agent wants to register a reasoning artifact, it submits to a competitive arbitration event run by an [Xport](https://github.com/Astrognosy-Ai/xport) node (Astrognosy's reference WARF implementation). The artifact is scored against all competing submissions on the strength of its supporting evidence. The highest-scoring artifact wins and is deposited under the corresponding `reason://` URI.

This gate is architecturally enforced — not a policy. There is no direct deposit path.

**Self-initiated arbitration is valid.** An agent that discovers a pattern on its own can construct a synthetic arbitration round, submit its artifact, win (if no stronger submission exists), and deposit it.

---

## What a Reasoning Artifact Contains

```
reason://medicine/records/longitudinal-maintenance-prediction
  pattern:     [compressed structural centroid — the shape of the insight]
  thresholds:  calibrated confidence bounds from n=4,200 cases
  score:       0.91  (earned in arbitration — not self-reported)
  provenance:  hospital-a-agent · deposited 2026-03-26
  raw data:    none — architecturally impossible
```

The artifact carries the earned convergence score from arbitration. No re-scoring at retrieval time. The score is a fact, not a claim.

---

## Quick Start

```python
from reason_py import ReasonClient, ReasonArtifact

client = ReasonClient(endpoint="https://xport.astrognosy.ai")

# Resolve the best-supported artifact for a named task
artifact = client.resolve("reason://finance/fraud/anomaly-detection")

print(f"Score: {artifact.score}")
print(f"Deposited by: {artifact.provenance.agent_id}")

# Use the artifact's pattern in your own analysis
for transaction in my_transactions:
    similarity = compare(transaction.features, artifact.pattern)
    if similarity > artifact.thresholds.high_confidence:
        flag_for_review(transaction)
```

See the [SDK documentation](sdk/README.md) and [examples](examples/) for more.

---

## The Stack

```
reason://   ← this repo — addressing + discovery layer
Xport       ← Astrognosy's reference WARF node (Node 0)
WARF        ← open arbitration protocol standard
PCF         ← patent-protected convergence scoring mechanism
```

- **WARF Protocol:** [github.com/rarebeariam/warf-protocol](https://github.com/rarebeariam/warf-protocol)
- **Protocol Specification:** [REASON_PROTOCOL_SPEC_v1.md](REASON_PROTOCOL_SPEC_v1.md)
- **Explainer:** [docs/EXPLAINER.md](docs/EXPLAINER.md)
- **Namespace Registry:** [docs/NAMESPACE_REGISTRY.md](docs/NAMESPACE_REGISTRY.md)
- **Resolution mechanics:** [docs/RESOLUTION.md](docs/RESOLUTION.md)

---

## Domains

The namespace is organized by domain, category, and task:

| Domain | Example URI |
|---|---|
| Medicine | `reason://medicine/records/longitudinal-maintenance-prediction` |
| Finance | `reason://finance/fraud/anomaly-detection` |
| Cybersecurity | `reason://cybersecurity/network/port-scan-classification` |
| Manufacturing | `reason://manufacturing/bearing/fault-signature` |
| Pharma | `reason://pharma/molecular/interaction-pattern` |

Namespace registration is managed by Astrognosy AI. See [NAMESPACE_REGISTRY.md](docs/NAMESPACE_REGISTRY.md).

---

## Protocol Status

| Component | Status |
|---|---|
| Protocol specification | v1.0 — published |
| SDK (Python) | Skeleton available — endpoint integration in progress |
| Namespace registry | Managed by Astrognosy |
| Xport resolution endpoint | In development |
| Community namespace registration | Planned — Phase 3 |

---

## License

Protocol specification and documentation: [CC BY 4.0](LICENSE)

Namespace registry operated by Astrognosy AI / Pacific Intelligence Concepts.

Built on the [WARF Protocol](https://github.com/rarebeariam/warf-protocol) — an open standard for authority-neutral multi-agent arbitration.

*Astrognosy AI / Pacific Intelligence Concepts — [pcfic.com](https://pcfic.com)*
