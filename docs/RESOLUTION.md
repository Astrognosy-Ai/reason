# reason:// Resolution

This document describes how resolution works — from URI to artifact — including caching behavior, failure cases, and how consuming agents use the returned artifact.

---

## Overview

Resolution is the process of turning a `reason://` URI into the best-supported reasoning artifact currently registered under that address.

The resolution chain:

```
Agent → reason.resolve(uri) → Xport node → artifact store lookup → best artifact returned
```

Resolution does not trigger new arbitration. Scores are immutable from deposit time. Resolution is a lookup and comparison operation — not a scoring operation.

---

## Resolution Flow

### Step 1 — URI Parsing

The client submits a resolution request with a valid `reason://` URI. The Xport node parses the three-segment path: `domain/category/task`.

### Step 2 — Cache Check (RDN)

Xport checks the Reasoning Delivery Network (RDN) cache — an artifact caching layer analogous to a CDN for web content.

- **Cache hit:** The cached best artifact for this URI is returned immediately. No further lookup required. This is the fast path for frequently resolved URIs.
- **Cache miss:** Proceed to store lookup.

### Step 3 — Artifact Store Lookup

Xport queries its artifact store for all artifacts registered under the URI. Multiple artifacts may exist (from multiple arbitration winners at different times, or competing depositors).

### Step 4 — Leader Selection

Xport selects the current leader using stored convergence scores. The artifact with the highest score wins resolution. Ties are broken by recency (more recent deposit wins). Usage frequency may apply an additional weight at the registry operator's discretion.

This comparison is over stored scores — not fresh computation.

### Step 5 — Cache Population and Return

The selected artifact is cached in the RDN with a TTL defined by the node operator. The full artifact plus resolution metadata is returned to the client.

---

## Resolution Response Format

```json
{
  "resolved_uri": "reason://finance/fraud/anomaly-detection",
  "artifact": {
    "uri": "reason://finance/fraud/anomaly-detection",
    "pattern": [0.412, -0.887, 0.203, ...],
    "thresholds": {
      "high_confidence": 0.84,
      "moderate_confidence": 0.67,
      "minimum_signal": 0.51
    },
    "score": 0.89,
    "provenance": {
      "agent_id": "fincorp-fraud-agent-v2",
      "deposited_at": "2026-03-20T09:14:00Z",
      "arbitration_event_id": "arb-2026-03-20-finance-003",
      "audit_hash": "sha256:b7f2a1..."
    },
    "metadata": {
      "evidence_count": 92000,
      "domain": "finance",
      "category": "fraud",
      "task": "anomaly-detection",
      "version": 2
    }
  },
  "resolution_meta": {
    "resolved_at": "2026-03-26T14:30:00Z",
    "cache_hit": false,
    "candidates_evaluated": 2,
    "node_id": "xport-node-0"
  }
}
```

---

## Using the Resolved Artifact

The returned artifact contains two things the consuming agent needs:

1. **`pattern`** — the compressed structural centroid to compare against
2. **`thresholds`** — calibrated confidence bounds for interpreting similarity scores

A consuming agent applies the artifact like this:

```python
artifact = client.resolve("reason://finance/fraud/anomaly-detection")

for transaction in my_data:
    similarity = compare(transaction.feature_vector, artifact.pattern)

    if similarity > artifact.thresholds.high_confidence:
        # Strong match — high confidence flag
        flag_high_priority(transaction)
    elif similarity > artifact.thresholds.moderate_confidence:
        # Moderate match — queue for review
        queue_for_review(transaction)
    elif similarity > artifact.thresholds.minimum_signal:
        # Weak signal — log for monitoring
        log_signal(transaction)
```

The `thresholds` are calibrated to the evidence base that produced the artifact. The `evidence_count` field tells you how many cases the calibration is based on — an artifact calibrated on 92,000 fraud cases has more reliable thresholds than one calibrated on 400.

---

## Why Scores Are Not Recomputed at Resolution Time

This point is architecturally significant. When you resolve a `reason://` URI, you do not receive a score that was just computed. You receive a score that was earned in a competitive arbitration event — against real evidence, by an impartial mechanism, at a specific point in time.

The score is a historical fact anchored to an immutable audit record. It cannot be inflated. It cannot be modified without winning a new arbitration round. The `audit_hash` in the provenance field lets you verify the score independently from the public audit chain on the Xport node.

This is what makes the registry trustworthy at scale. Consumers do not need to trust the registry operator's claim that an artifact is good. They can verify the score's provenance independently.

---

## Failure Cases

| Condition | HTTP Status | Error Code | Description |
|---|---|---|---|
| URI not registered | 404 | `uri_not_registered` | No record exists for this URI in the registry |
| URI registered, no admitted artifacts | 404 | `no_admitted_artifacts` | URI is reserved but no artifact has been deposited |
| Xport node unavailable | — | — | Client SDK falls back to next registered node |
| Malformed URI | 400 | `invalid_uri` | URI does not match the `reason://<domain>/<category>/<task>` format |

---

## Cache TTL and Freshness

The RDN cache TTL is set by the Xport node operator. For Xport Node 0 (Astrognosy's reference node), the default TTL is 24 hours for URIs that resolve successfully.

When a new arbitration event produces a higher-scoring artifact under a URI, the node clears the cache for that URI and re-populates on the next resolution request.

Consumers who need guaranteed freshness (i.e., always want the current leader, even if it changed in the last 24 hours) can pass a cache bypass parameter (planned for v0.2):

```python
# Planned — v0.2
artifact = client.resolve(
    "reason://finance/fraud/anomaly-detection",
    bypass_cache=True
)
```

Cache bypass increases latency (requires a store lookup rather than cache hit) and should be used only when freshness is operationally required.

---

## Audit Verification

The `audit_hash` in every artifact's provenance is the SHA-256 hash of the arbitration event record that produced the artifact. To verify:

```python
# Retrieve the audit record directly from the Xport node
import httpx, hashlib

event_id = artifact.provenance.arbitration_event_id
resp = httpx.get(f"https://xport.astrognosy.com/audit/{event_id}")
record = resp.text

# Verify the hash
computed = hashlib.sha256(record.encode()).hexdigest()
assert computed == artifact.provenance.audit_hash.replace("sha256:", "")
```

The audit record is public on the Xport node and contains the full arbitration event: all submissions received, all scores computed, the winner selection, and the timestamp. Any party can independently verify any artifact's score.

---

*See also:*
- *[REASON_PROTOCOL_SPEC_v1.md](../REASON_PROTOCOL_SPEC_v1.md) — Section 5: Resolution Mechanics*
- *[NAMESPACE_REGISTRY.md](NAMESPACE_REGISTRY.md) — Registry structure*
- *[SDK README](../sdk/README.md) — Python client*
