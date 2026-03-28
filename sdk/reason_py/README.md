# reason-py

Official Python client for [reason://](https://github.com/astrognosy/reason) — the reasoning infrastructure for the agentic internet.

```bash
pip install reason-py
```

## Quickstart

```python
from reason_py import ReasonClient

client = ReasonClient()

# Resolve a validated reasoning artifact
artifact = client.resolve("reason://finance/fraud/synthetic-identity-temporal-motif")

# Apply it locally — nothing leaves your environment
for transaction in my_transactions:
    similarity = client.compare(transaction.embedding, artifact)
    if similarity > artifact.thresholds.high_confidence:
        flag(transaction)
```

## Point at your own node

```python
client = ReasonClient(endpoint="http://localhost:8080")
```

## What transfers

The artifact contains only the non-invertible structural centroid of a validated pattern. No raw data. No model weights. Reconstruction rate empirically measured at r = 0.0149 (< 1.5% of original signal recoverable).

## License

CC BY 4.0 — Jacob Westerbeck / [Astrognosy AI](https://astrognosy.com)
