"""
reason_py — Official Python client for the reason:// protocol.

    from reason_py import ReasonClient

    client = ReasonClient()
    artifact = client.resolve("reason://finance/fraud/synthetic-identity-temporal-motif")

    for transaction in my_transactions:
        similarity = client.compare(transaction.embedding, artifact)
        if similarity > artifact.thresholds.high_confidence:
            flag(transaction)
"""

from reason_py.client import ReasonClient
from reason_py.models import (
    ReasonArtifact,
    ArtifactThresholds,
    ArtifactProvenance,
    ArtifactMetadata,
)

__version__ = "0.1.0"
__all__ = [
    "ReasonClient",
    "ReasonArtifact",
    "ArtifactThresholds",
    "ArtifactProvenance",
    "ArtifactMetadata",
]
