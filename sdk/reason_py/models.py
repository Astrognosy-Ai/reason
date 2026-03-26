"""
Data models for the reason:// protocol.

These models represent the artifacts stored in and retrieved from
the reason:// namespace registry.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ArtifactThresholds:
    """
    Calibrated confidence bounds for interpreting similarity scores
    against a reasoning artifact's pattern.

    These thresholds are derived from the evidence base that produced
    the artifact and calibrated during the arbitration process.

    Usage:
        similarity = compare(my_data, artifact.pattern)
        if similarity > artifact.thresholds.high_confidence:
            # Strong match — act with high confidence
            ...
        elif similarity > artifact.thresholds.moderate_confidence:
            # Moderate match — review
            ...
    """
    high_confidence: float
    moderate_confidence: float
    minimum_signal: float

    def classify(self, similarity_score: float) -> str:
        """
        Classify a similarity score against this artifact's calibrated thresholds.

        Returns one of: "high_confidence", "moderate_confidence",
                        "minimum_signal", "no_signal"
        """
        if similarity_score >= self.high_confidence:
            return "high_confidence"
        elif similarity_score >= self.moderate_confidence:
            return "moderate_confidence"
        elif similarity_score >= self.minimum_signal:
            return "minimum_signal"
        else:
            return "no_signal"


@dataclass
class ArtifactProvenance:
    """
    Immutable audit record for a reasoning artifact.

    Records which agent deposited the artifact, when, and links the
    artifact to the specific arbitration event that admitted it.
    The audit_hash can be independently verified against the Xport
    node's public audit chain.
    """
    agent_id: str
    deposited_at: str          # ISO 8601 timestamp
    arbitration_event_id: str
    audit_hash: str            # sha256:<hex> — verifiable against node audit chain


@dataclass
class ArtifactMetadata:
    """
    Supplementary metadata for a reasoning artifact.

    evidence_count: number of cases used to produce and calibrate
    the pattern and thresholds. Higher counts generally indicate
    more reliable calibration.
    """
    evidence_count: int
    domain: str
    category: str
    task: str
    version: int = 1


@dataclass
class ReasonArtifact:
    """
    A reasoning artifact retrieved from the reason:// registry.

    An artifact contains the compressed structural pattern learned by
    the depositing agent, calibrated thresholds for interpreting
    similarity scores, the convergence score earned in arbitration,
    and full provenance information.

    The pattern is a mathematically non-invertible representation of
    the learned insight. It encodes the shape of the pattern — not
    the data that produced it. Raw source data cannot be recovered
    from the pattern.

    Attributes:
        uri: The reason:// URI this artifact is registered under.
        pattern: Compressed structural centroid (list of floats).
        thresholds: Calibrated confidence bounds.
        score: Convergence score earned in arbitration. Immutable.
        provenance: Audit record linking to the arbitration event.
        metadata: Supplementary information (evidence count, domain, etc).
    """
    uri: str
    pattern: List[float]
    thresholds: ArtifactThresholds
    score: float
    provenance: ArtifactProvenance
    metadata: ArtifactMetadata

    def __repr__(self) -> str:
        return (
            f"ReasonArtifact("
            f"uri={self.uri!r}, "
            f"score={self.score:.3f}, "
            f"agent={self.provenance.agent_id!r}, "
            f"evidence_count={self.metadata.evidence_count}"
            f")"
        )

    @classmethod
    def from_dict(cls, data: dict) -> "ReasonArtifact":
        """Deserialize a ReasonArtifact from a resolution response dict."""
        thresholds = ArtifactThresholds(
            high_confidence=data["thresholds"]["high_confidence"],
            moderate_confidence=data["thresholds"]["moderate_confidence"],
            minimum_signal=data["thresholds"]["minimum_signal"],
        )
        provenance = ArtifactProvenance(
            agent_id=data["provenance"]["agent_id"],
            deposited_at=data["provenance"]["deposited_at"],
            arbitration_event_id=data["provenance"]["arbitration_event_id"],
            audit_hash=data["provenance"]["audit_hash"],
        )
        metadata = ArtifactMetadata(
            evidence_count=data["metadata"]["evidence_count"],
            domain=data["metadata"]["domain"],
            category=data["metadata"]["category"],
            task=data["metadata"]["task"],
            version=data["metadata"].get("version", 1),
        )
        return cls(
            uri=data["uri"],
            pattern=data["pattern"],
            thresholds=thresholds,
            score=data["score"],
            provenance=provenance,
            metadata=metadata,
        )

    def to_dict(self) -> dict:
        """Serialize this artifact to a dict (for submission in registration)."""
        return {
            "uri": self.uri,
            "pattern": self.pattern,
            "thresholds": {
                "high_confidence": self.thresholds.high_confidence,
                "moderate_confidence": self.thresholds.moderate_confidence,
                "minimum_signal": self.thresholds.minimum_signal,
            },
            "score": self.score,
            "provenance": {
                "agent_id": self.provenance.agent_id,
                "deposited_at": self.provenance.deposited_at,
                "arbitration_event_id": self.provenance.arbitration_event_id,
                "audit_hash": self.provenance.audit_hash,
            },
            "metadata": {
                "evidence_count": self.metadata.evidence_count,
                "domain": self.metadata.domain,
                "category": self.metadata.category,
                "task": self.metadata.task,
                "version": self.metadata.version,
            },
        }
