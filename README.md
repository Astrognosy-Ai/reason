# reason:// — Reasoning Infrastructure for the Agentic Internet

**The HTTP for learned intelligence.**

Share structural reasoning patterns across silos — without sharing data, models, or weights.

- **Privacy** — architecturally guaranteed (non-invertible centroids, r=0.0149 reconstruction bound)
- **Trust** — only validated winners via live WARF arbitration
- **One line** — `artifact = client.resolve("reason://medicine/records/longitudinal-maintenance-prediction")`

**Status**: v0.1 Bootstrap — Spec + SDK + Reference Node live.

---

## Try it live

**[Open the WARF + reason:// Demo →](https://warfdemo.streamlit.app)**

Deposit a structural artifact → resolve it from another agent → watch the privacy guarantee in action.

---

## Quickstart

```bash
pip install reason-py
```

```python
from reason_py import ReasonClient

client = ReasonClient()

# Resolve a named reasoning artifact
artifact = client.resolve("reason://finance/fraud/synthetic-identity-temporal-motif")

# Apply it to your local data — nothing leaves your environment
for transaction in my_transactions:
    similarity = client.compare(transaction.embedding, artifact)
    if similarity > artifact.thresholds.high_confidence:
        flag(transaction)
```

See [`examples/`](examples/) for hospital, bank fraud, defense, and pharma use cases.

---

## What is reason://

Every AI agent operating in a regulated environment is a silo. Hospital A's agent learns a fraud pattern. Hospital B's agent solves the same problem from scratch. The insight can't travel — data can't be shared (HIPAA), models can't be shared (proprietary), weights can't be shared (they encode the data).

`reason://` is the infrastructure layer that fixes this.

An agent that discovers a reasoning pattern deposits a **compressed structural artifact** — the shape of the insight, mathematically separated from the data that produced it — under a structured address:

```
reason://medicine/records/longitudinal-maintenance-prediction
reason://finance/fraud/synthetic-identity-temporal-motif
reason://cybersecurity/network/port-scan-classification
```

Any agent anywhere resolves that address in one line. No data crosses any boundary. No model is exposed. The privacy guarantee is structural — the artifact schema has no field for raw data, and the representation is mathematically non-invertible.

**The only way an artifact enters the registry is by winning a live WARF arbitration round.** The registry is a hall of validated winners, not a submission box.

---

## The Stack

```
reason://   ← this protocol — naming, quality gating, resolution
Xport       ← Astrognosy's reference WARF node — runs arbitration, stores artifacts
WARF        ← open arbitration protocol — rules for competitive evaluation
PCF         ← patent-protected convergence scoring mechanism — the math
```

`reason://` is to agent intelligence what DNS is to network addresses. Xport is the reference resolver. WARF is the routing protocol. PCF is the scoring engine.

---

## Protocol

| Property | Value |
|---|---|
| License | CC BY 4.0 |
| URI format | `reason://<domain>/<category>/<task>` |
| Artifact schema | JSON — no raw data fields, ever |
| Registry entry gate | WARF arbitration winner only |
| Reconstruction bound | r = 0.0149 (empirical, P2P study n=4,200) |
| Audit | SHA-256 chained, publicly verifiable |

Full spec: [`REASON_PROTOCOL_SPEC_v1.md`](REASON_PROTOCOL_SPEC_v1.md)

---

## SDK

**Python** — `pip install reason-py` → [`sdk/reason_py/`](sdk/reason_py/)

**TypeScript** — [`sdk/reason_ts/reason.ts`](sdk/reason_ts/reason.ts)

---

## Run a Reference Node

```bash
cd warf-node
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8080
```

Point your client at it:

```python
client = ReasonClient(endpoint="http://localhost:8080")
```

Docker:

```bash
docker build -t reason-node warf-node/
docker run -p 8080:8080 reason-node
```

---

## IETF

Internet-Draft in progress: [`docs/ietf/draft-00.md`](docs/ietf/draft-00.md)

`draft-jwesterbeck-reason-reasoning-artifact-federation-00`

The arbitration layer is defined in a separate draft: `draft-westerbeck-warf-protocol-00` — [WARF Protocol repo](https://github.com/Astrognosy-Ai/warf-protocol)

---

## Governance

Bootstrap (now → Q4 2026): Astrognosy operates the registry.
Transition (Q4 2026): IETF Working Group, hand off to neutral foundation.
Community (2027+): DAO-style governance for new top-level namespaces.

See [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) for the full model including economic layer activation.

---

## Commercial

This repo is the open protocol. The **Pacific platform** (pcfic.com) provides self-hosted WARF nodes, certified artifact pipelines, and production-scale infrastructure for enterprise deployments.

---

Built by Jacob Westerbeck — [Astrognosy AI](https://astrognosy.com) · [jacob@pcfic.com](mailto:jacob@pcfic.com)
