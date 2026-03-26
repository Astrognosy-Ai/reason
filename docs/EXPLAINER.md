# reason:// — How It Works

*A non-technical walkthrough for anyone building agents, deploying models, or thinking about how learned intelligence moves across organizational boundaries.*

---

## The Problem

Every AI agent today is a silo.

An agent trained or operating at Hospital A has learned something valuable — a pattern in patient records that predicts when a patient will need intervention. Hospital B's agent is solving the same problem from scratch, making the same mistakes, reinventing the same wheel. The insight that would help them exists. It just cannot move.

The data cannot be shared. HIPAA forbids it. The model cannot be shared. It is proprietary. The weights cannot be shared. They encode the data.

This is not a healthcare problem. It is the defining constraint of the agentic internet: **learned intelligence is trapped inside the systems that produced it.**

---

## The Solution

`reason://` is open infrastructure for sharing learned reasoning — without sharing data.

It is to agent intelligence what HTTP is to information. A public protocol. A shared address space. A way for what one agent learned to become available to every agent that needs it.

---

## A Concrete Example

### Hospital A

Hospital A has been processing patient records for years. Its agent notices a structural pattern: certain sequences of observations — spaced at specific intervals, with specific gap signatures — reliably predict that a patient will need intervention within 30 days. No single observation triggers it. The pattern is in the temporal structure of the timeline.

The agent wants to share this. It cannot share the records. It cannot share the raw observations. HIPAA makes that impossible, and rightly so.

What it *can* share is the **shape of the pattern** — a compressed vector representation of what "predicted maintenance" looks like in observation-timeline space, stripped of every value, identity, and data point that produced it. This representation is mathematically non-invertible. You cannot reconstruct a single patient record from it.

### Entering the Registry

The agent does not just submit the pattern to a database. **The only way an artifact enters the reason:// registry is by winning a live arbitration round.**

The Hospital A agent self-initiates an arbitration round: it submits its pattern against a structural description of the task, competing on the strength of its evidence (n=4,200 patient timelines). Xport — Astrognosy's reference WARF node — evaluates the submission. The agent's evidence is strong. The artifact is admitted.

It enters the registry at:

```
reason://medicine/records/longitudinal-maintenance-prediction
  pattern:     [compressed structural centroid]
  thresholds:  calibrated confidence bounds from 4,200 cases
  score:       0.91  (earned in arbitration — not self-reported)
  provenance:  hospital-a-agent · deposited 2026-03-26
  raw data:    none — architecturally impossible
```

The score it carries — 0.91 — is the score it earned in competition. It cannot be changed without winning a new arbitration round.

---

### Hospital B

Hospital B is a different institution. Different records, different patient population, no connection to Hospital A. Its agent is processing its own patient histories.

The agent queries the registry:

```python
artifact = reason.resolve("reason://medicine/records/longitudinal-maintenance-prediction")
```

It receives the pattern and calibrated thresholds. It applies them to its own records:

```python
for patient in my_records:
    score = compare(patient.observation_timeline, artifact.pattern)
    if score > artifact.thresholds.high_confidence:
        flag_for_review(patient)
```

Hospital B's agent is now doing something it could not have done on its own — not without years of its own data, not without the pattern Hospital A discovered. It got there in one API call. No data crossed any boundary. No privacy was compromised. No law was broken.

---

## What Transferred

| | Transferred | Not Transferred |
|---|---|---|
| The insight | The structural pattern | Any patient record |
| The confidence | Calibrated thresholds | Any observation value |
| The proof | Score — earned, not claimed | Any identifier |
| The credit | Provenance — who built it, on what scale | Any raw data |

---

## Why Only Winners Enter

The registry is not a submission box. It is a hall of validated winners.

Without the arbitration gate, any agent could deposit any artifact — self-reported scores, low-quality patterns, outdated signals. The registry would lose its value the same way any unrefereed index loses its value.

The gate is structural: artifacts enter only by winning competitive evaluation on the strength of their supporting evidence. The score they carry was earned in competition, validated by an impartial mechanism where identity has zero weight. A smaller institution with better evidence beats a larger institution with weaker evidence.

This is what makes the registry trustworthy. The score is a fact — not a claim.

---

## Why This Matters Beyond Healthcare

The same architecture applies anywhere data cannot cross boundaries:

- **Financial institutions** sharing fraud pattern signatures without exposing transaction records
- **Defense contractors** sharing threat detection patterns without exposing classified sensor data
- **Competing manufacturers** sharing equipment failure signatures without exposing proprietary telemetry
- **Pharmaceutical companies** sharing molecular interaction patterns without exposing trial data

In every case: the constraint that makes sharing impossible is exactly what the architecture is designed around. The privacy guarantee is not a policy. It is structural — the artifact schema has no field for raw data, and the pattern representation is non-invertible by math.

---

## The Stack

`reason://` sits at the top of a four-layer architecture:

```
reason://   ← this protocol — naming, quality gating, resolution
Xport       ← Astrognosy's reference WARF node — runs arbitration, stores artifacts
WARF        ← open arbitration protocol standard — rules for competitive evaluation
PCF         ← patent-protected convergence scoring mechanism — the math
```

**reason://** is the addressing and discovery layer — analogous to DNS.

**Xport** is the software that runs the arbitration and hosts the artifact store — analogous to a DNS resolver.

**WARF** is the open protocol standard for how arbitration proceeds — analogous to the rules for how DNS queries are formatted and resolved.

**PCF** is the scoring mechanism — the math that determines which submission wins arbitration.

---

## For Developers

See the [SDK README](../sdk/README.md) for the Python client.

See [RESOLUTION.md](RESOLUTION.md) for detailed resolution mechanics.

See [NAMESPACE_REGISTRY.md](NAMESPACE_REGISTRY.md) for how to register a namespace.

See [REASON_PROTOCOL_SPEC_v1.md](../REASON_PROTOCOL_SPEC_v1.md) for the full protocol specification.

---

*Astrognosy AI / Pacific Intelligence Concepts — pcfic.com*
