
# reason:// Protocol Specification v0.1

**Address format**: `reason://<namespace>/<category>/<specific-pattern>`

**Artifact schema** (JSON):
- `address`
- `pattern`: List[float] (non-invertible structural centroid)
- `thresholds`: Dict[str, float]
- `score`: float (WARF arbitration score)
- `confidence`: float
- `provenance`: Dict[str, str]
- `metadata`: Dict[str, Any]

Only artifacts that win a live WARF round are admitted.
Full WARF arbitration rules and tokenized corpus format are defined in the reference node.

CC BY 4.0 — see README.md for implementation details.
