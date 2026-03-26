# reason:// Namespace Registry

The reason:// namespace registry is operated by Astrognosy AI. This document describes the namespace structure, approved top-level domains, structural rules, and how to request a new namespace path.

---

## Structure

A reason:// URI has three segments:

```
reason://<domain>/<category>/<task>
```

All three segments are required. No URI is valid without all three.

| Segment | Role |
|---|---|
| `domain` | Top-level knowledge area |
| `category` | Sub-area within the domain |
| `task` | Specific bounded capability |

All segments are lowercase. Hyphens are the only permitted word separator — no underscores, no camelCase, no spaces.

---

## Approved Domains

| Domain | Description |
|---|---|
| `medicine` | Clinical, records, imaging, diagnostics, pharmacology |
| `finance` | Fraud, credit, markets, risk, compliance |
| `cybersecurity` | Network, endpoint, application, cloud security |
| `manufacturing` | Bearing, motor, structural, quality control |
| `pharma` | Molecular, clinical, regulatory, supply chain |
| `defense` | Sensor, signal, classification (access-controlled) |
| `energy` | Grid, renewable, fault detection, consumption |
| `logistics` | Routing, demand forecasting, supply chain optimization |
| `agriculture` | Crop, soil, yield, pest detection |
| `climate` | Atmospheric, oceanic, land surface patterns |

New domains require registry approval. Contact Astrognosy via GitHub issue to propose a new top-level domain.

---

## Registered Namespaces

### medicine

| URI | Status | Description |
|---|---|---|
| `reason://medicine/records/longitudinal-maintenance-prediction` | Active | Predicts patient intervention needs from observation timeline patterns |
| `reason://medicine/imaging/lesion-boundary-detection` | Reserved | Structural boundary patterns in medical imaging |
| `reason://medicine/symptom/triage-model` | Reserved | Symptom cluster patterns for triage prioritization |

### finance

| URI | Status | Description |
|---|---|---|
| `reason://finance/fraud/anomaly-detection` | Active | Transaction anomaly patterns for fraud identification |
| `reason://finance/credit/default-risk-pattern` | Reserved | Structural patterns in credit behavior preceding default |
| `reason://finance/aml/transaction-chain-pattern` | Reserved | Multi-hop transaction chain patterns for AML |

### cybersecurity

| URI | Status | Description |
|---|---|---|
| `reason://cybersecurity/network/port-scan-classification` | Active | Network traffic patterns indicating port scanning activity |
| `reason://cybersecurity/network/intrusion-detection` | Active | Structural intrusion signatures from network flow data |
| `reason://cybersecurity/endpoint/lateral-movement-pattern` | Reserved | Endpoint behavior patterns associated with lateral movement |

### manufacturing

| URI | Status | Description |
|---|---|---|
| `reason://manufacturing/bearing/fault-signature` | Active | Vibration signal patterns predicting bearing failure |
| `reason://manufacturing/motor/vibration-anomaly` | Active | Motor vibration anomaly patterns from multi-signal data |
| `reason://manufacturing/weld/quality-pattern` | Reserved | Acoustic emission patterns for weld quality assessment |

---

## Status Definitions

| Status | Meaning |
|---|---|
| `Active` | At least one artifact admitted via arbitration; URI resolves |
| `Reserved` | URI approved and registered; no artifact admitted yet; awaiting first arbitration |
| `Deprecated` | URI no longer accepting new artifacts; existing artifacts remain resolvable |

---

## Requesting a Namespace

To request a new `reason://` URI path:

1. Open a GitHub issue in this repository with the title: `[namespace-request] reason://<domain>/<category>/<task>`
2. Include:
   - **Full URI:** The complete proposed URI path
   - **Description:** A one-sentence description of the capability this URI will represent
   - **Domain justification:** Why this fits under the proposed domain and category
   - **Scope confirmation:** Confirmation that this task is not duplicative of an existing URI
   - **Arbitration commitment:** Commitment to submit at least one artifact via arbitration within 90 days of approval
3. The registry operator will review within 14 business days

### Evaluation Criteria

- The task is clearly scoped and bounded — not an entire research field
- The domain/category structure is consistent with the existing hierarchy
- The URI is not duplicative of or ambiguous with an existing URI
- The task represents a real, deployed use case (not hypothetical)

---

## Structural Rules

1. All segments must be lowercase ASCII
2. Hyphens are the only permitted word separator
3. Each segment must be 3–64 characters
4. No special characters other than hyphens
5. The full URI must be unique in the registry
6. Domain must be an approved top-level domain or a newly approved expansion
7. Category must describe a coherent sub-area — not duplicate the domain name
8. Task must name a specific capability, not a broad field

### Examples of Valid URIs

```
reason://medicine/records/longitudinal-maintenance-prediction   ✓
reason://finance/fraud/anomaly-detection                        ✓
reason://cybersecurity/network/port-scan-classification         ✓
```

### Examples of Invalid URIs

```
reason://medicine/medicine/detection        ✗  (category duplicates domain)
reason://Finance/Fraud/AnomalyDetection     ✗  (not lowercase, no hyphens)
reason://ai/general/intelligence            ✗  (task too broad)
reason://medicine/records/                  ✗  (missing task segment)
```

---

## Registry Stability Commitment

Astrognosy AI commits to:

- Not repurposing or invalidating URIs that have received at least one resolution request
- Maintaining resolution service for any URI with at least one admitted artifact
- Providing 180 days advance notice before any breaking change to the URI structure or resolution protocol
- Publishing the full registry index in this file, updated with each admission

---

## Full Registry Index

The complete current registry index is maintained in this document. The `Active` and `Reserved` tables above constitute the current registry state as of the date of the last commit.

Registry last updated: 2026-03-26

---

*Namespace registry operated by Astrognosy AI / Pacific Intelligence Concepts*
*pcfic.com*
