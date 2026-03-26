"""
reason_py — Python SDK for the reason:// protocol

Resolve and register reasoning artifacts via the reason:// namespace.

Usage:
    from reason_py import ReasonClient, ReasonArtifact

    client = ReasonClient(endpoint="https://xport.astrognosy.ai")
    artifact = client.resolve("reason://finance/fraud/anomaly-detection")
    print(artifact.score)

See README.md for full documentation.
"""

from .client import ReasonClient
from .models import ReasonArtifact, ArtifactThresholds, ArtifactProvenance, ArtifactMetadata

__version__ = "0.1.0"
__all__ = [
    "ReasonClient",
    "ReasonArtifact",
    "ArtifactThresholds",
    "ArtifactProvenance",
    "ArtifactMetadata",
]
