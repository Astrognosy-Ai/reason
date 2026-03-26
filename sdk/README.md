# reason_py — Python SDK

The `reason_py` SDK provides a Python client for resolving and registering reasoning artifacts via the reason:// namespace protocol.

## Installation

```bash
pip install reason-py
```

Or install directly from source:

```bash
git clone https://github.com/Astrognosy-Ai/reason.git
cd reason/sdk
pip install -e .
```

**Python 3.8+ required.** No external dependencies — uses only the standard library.

---

## Quick Start

```python
from reason_py import ReasonClient

# Connect to the reference Xport node
client = ReasonClient(endpoint="https://xport.astrognosy.ai")

# Resolve a named reasoning artifact
artifact = client.resolve("reason://finance/fraud/anomaly-detection")

print(f"Score: {artifact.score}")
print(f"Deposited by: {artifact.provenance.agent_id}")
print(f"Evidence: {artifact.metadata.evidence_count} cases")

# Apply the artifact's pattern to your own data
for transaction in my_transactions:
    similarity = my_compare_fn(transaction.features, artifact.pattern)
    tier = artifact.thresholds.classify(similarity)

    if tier == "high_confidence":
        flag_high_priority(transaction)
    elif tier == "moderate_confidence":
        queue_for_review(transaction)
```

---

## API Reference

### `ReasonClient`

```python
client = ReasonClient(
    endpoint="https://xport.astrognosy.ai",  # Xport node URL
    timeout=30,                               # request timeout in seconds
    api_key=None,                             # optional API key
)
```

#### `resolve(uri, bypass_cache=False) -> ReasonArtifact`

Resolve a `reason://` URI to the best-supported artifact currently registered under that address.

- `uri` — A valid reason:// URI. Format: `reason://<domain>/<category>/<task>`
- `bypass_cache` — Skip the node's RDN cache and perform a fresh store lookup. Default: `False`.

Returns a `ReasonArtifact`. Raises `ReasonURIError` if the URI is malformed. Raises `ReasonResolutionError` if the URI is not found or the node returns an error.

```python
artifact = client.resolve("reason://medicine/records/longitudinal-maintenance-prediction")
```

#### `register(uri, artifact) -> bool`

Register a `ReasonArtifact` under a `reason://` URI. The artifact must have won a live arbitration round — the Xport node verifies the `arbitration_event_id` and `audit_hash` in the artifact's provenance before accepting the registration.

Returns `True` if registration succeeded.

```python
success = client.register("reason://manufacturing/bearing/fault-signature", my_artifact)
```

#### `get_audit_record(arbitration_event_id) -> str`

Retrieve the raw audit record for an arbitration event. Use this to independently verify an artifact's score against its `audit_hash`.

```python
record = client.get_audit_record(artifact.provenance.arbitration_event_id)

import hashlib
computed = "sha256:" + hashlib.sha256(record.encode()).hexdigest()
assert computed == artifact.provenance.audit_hash
```

#### `list_artifacts(uri) -> List[ReasonArtifact]`

List all artifacts registered under a URI, ordered by score descending. The first item is the current resolution leader.

```python
all_artifacts = client.list_artifacts("reason://finance/fraud/anomaly-detection")
for a in all_artifacts:
    print(f"  {a.score:.3f}  {a.provenance.agent_id}")
```

---

### `ReasonArtifact`

The artifact returned by `resolve()`.

| Field | Type | Description |
|---|---|---|
| `uri` | `str` | The reason:// URI this artifact is registered under |
| `pattern` | `List[float]` | Compressed structural centroid — apply to your data |
| `thresholds` | `ArtifactThresholds` | Calibrated confidence bounds |
| `score` | `float` | Convergence score from arbitration (immutable) |
| `provenance` | `ArtifactProvenance` | Audit record — agent, timestamp, event ID, hash |
| `metadata` | `ArtifactMetadata` | Evidence count, domain, category, task, version |

### `ArtifactThresholds`

| Field | Type | Description |
|---|---|---|
| `high_confidence` | `float` | Strong match threshold |
| `moderate_confidence` | `float` | Moderate match threshold |
| `minimum_signal` | `float` | Weak signal threshold |

```python
# Method: classify a similarity score against calibrated thresholds
tier = artifact.thresholds.classify(0.87)
# Returns one of: "high_confidence", "moderate_confidence", "minimum_signal", "no_signal"
```

### `ArtifactProvenance`

| Field | Type | Description |
|---|---|---|
| `agent_id` | `str` | ID of the agent that deposited this artifact |
| `deposited_at` | `str` | ISO 8601 timestamp of deposit |
| `arbitration_event_id` | `str` | ID of the arbitration event that admitted the artifact |
| `audit_hash` | `str` | `sha256:<hex>` — verifiable against the node's audit chain |

---

## Error Handling

| Exception | When raised |
|---|---|
| `ReasonURIError` | URI is malformed (wrong format, uppercase, missing segments) |
| `ReasonResolutionError` | URI not found, no admitted artifacts, or node error during resolve |
| `ReasonRegistrationError` | Node rejected registration (arbitration not verified, etc.) |

```python
from reason_py import ReasonClient
from reason_py.client import ReasonURIError, ReasonResolutionError

client = ReasonClient()

try:
    artifact = client.resolve("reason://finance/fraud/anomaly-detection")
except ReasonURIError as e:
    print(f"Bad URI: {e}")
except ReasonResolutionError as e:
    print(f"Could not resolve: {e}")
```

---

## URI Format

```
reason://<domain>/<category>/<task>
```

- All segments lowercase
- Hyphens only — no underscores, no spaces, no camelCase
- All three segments required

```python
# Valid
client.resolve("reason://medicine/records/longitudinal-maintenance-prediction")
client.resolve("reason://finance/fraud/anomaly-detection")
client.resolve("reason://cybersecurity/network/port-scan-classification")

# Invalid — raises ReasonURIError
client.resolve("reason://Medicine/Records/Prediction")    # uppercase
client.resolve("reason://finance/fraud")                  # missing task segment
client.resolve("reason://finance/fraud_detection/all")    # underscore
```

---

## Examples

See the [examples/](../examples/) directory:

- [`hospital_example.py`](../examples/hospital_example.py) — Hospital A/B walkthrough
- [`finance_example.py`](../examples/finance_example.py) — Fraud detection pattern

---

*reason_py is part of the reason:// protocol — CC BY 4.0*
*Astrognosy AI / Pacific Intelligence Concepts — pcfic.com*
