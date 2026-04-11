"""
Unit tests for reason_py.client and reason_py.models.

No network I/O. No external deps. Run with:
    pytest sdk/reason_py/tests/test_client.py
"""

import math
import sys
import os

# Allow importing reason_py from the SDK directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from reason_py.client import ReasonClient, ReasonURIError
from reason_py.models import (
    ArtifactMetadata,
    ArtifactProvenance,
    ArtifactThresholds,
    ReasonArtifact,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_artifact(
    uri="reason://finance/fraud/anomaly-detection",
    pattern=None,
    score=0.82,
    audit_hash=None,
):
    if pattern is None:
        pattern = [0.1, 0.2, 0.3, 0.4]
    if audit_hash is None:
        audit_hash = "a" * 64
    return ReasonArtifact(
        uri=uri,
        pattern=pattern,
        thresholds=ArtifactThresholds(
            high_confidence=0.85,
            moderate_confidence=0.65,
            minimum_signal=0.45,
        ),
        score=score,
        provenance=ArtifactProvenance(
            agent_id="test-agent-0",
            deposited_at="2026-03-29T00:00:00Z",
            arbitration_event_id="abc123",
            audit_hash=audit_hash,
        ),
        metadata=ArtifactMetadata(
            evidence_count=10000,
            domain="finance",
            category="fraud",
            task="anomaly-detection",
        ),
    )


# ---------------------------------------------------------------------------
# URI validation
# ---------------------------------------------------------------------------

class TestURIValidation:
    def test_valid_uri(self):
        client = ReasonClient.__new__(ReasonClient)
        client._validate_uri("reason://finance/fraud/anomaly-detection")

    def test_valid_uri_with_hyphens(self):
        client = ReasonClient.__new__(ReasonClient)
        client._validate_uri("reason://cyber-security/network/port-scan-classification")

    def test_wrong_scheme(self):
        client = ReasonClient.__new__(ReasonClient)
        with pytest.raises(ReasonURIError):
            client._validate_uri("http://finance/fraud/anomaly-detection")

    def test_missing_segments(self):
        client = ReasonClient.__new__(ReasonClient)
        with pytest.raises(ReasonURIError):
            client._validate_uri("reason://finance/fraud")

    def test_uppercase_rejected(self):
        client = ReasonClient.__new__(ReasonClient)
        with pytest.raises(ReasonURIError):
            client._validate_uri("reason://Finance/fraud/anomaly-detection")

    def test_segment_64_chars_rejected(self):
        # 64-char segment: "a" + "b" * 63 = 64 chars — exceeds max of 63
        long_segment = "a" + "b" * 63
        assert len(long_segment) == 64
        client = ReasonClient.__new__(ReasonClient)
        with pytest.raises(ReasonURIError):
            client._validate_uri(f"reason://{long_segment}/fraud/anomaly-detection")

    def test_segment_63_chars_accepted(self):
        # 63-char segment: "a" + "b" * 62 = 63 chars — exactly at max
        max_segment = "a" + "b" * 62
        assert len(max_segment) == 63
        client = ReasonClient.__new__(ReasonClient)
        client._validate_uri(f"reason://{max_segment}/fraud/anomaly-detection")

    def test_single_char_segment_rejected(self):
        # reason://a/b/c — single-char segments are invalid (pattern requires {1,62} after first char)
        client = ReasonClient.__new__(ReasonClient)
        with pytest.raises(ReasonURIError):
            client._validate_uri("reason://a/b/c")

    def test_malformed_no_slashes(self):
        client = ReasonClient.__new__(ReasonClient)
        with pytest.raises(ReasonURIError):
            client._validate_uri("reason://financeFraudAnomalyDetection")

    def test_empty_string(self):
        client = ReasonClient.__new__(ReasonClient)
        with pytest.raises(ReasonURIError):
            client._validate_uri("")


# ---------------------------------------------------------------------------
# ReasonArtifact.from_dict roundtrip
# ---------------------------------------------------------------------------

class TestArtifactFromDict:
    def _sample_dict(self):
        return {
            "uri": "reason://finance/fraud/anomaly-detection",
            "pattern": [0.1, 0.2, 0.3],
            "thresholds": {
                "high_confidence": 0.85,
                "moderate_confidence": 0.65,
                "minimum_signal": 0.45,
            },
            "score": 0.82,
            "provenance": {
                "agent_id": "agent-0",
                "deposited_at": "2026-03-29T00:00:00Z",
                "arbitration_event_id": "evt-abc123",
                "audit_hash": "d" * 64,
            },
            "metadata": {
                "evidence_count": 92000,
                "domain": "finance",
                "category": "fraud",
                "task": "anomaly-detection",
                "version": 1,
            },
        }

    def test_roundtrip_preserves_uri(self):
        d = self._sample_dict()
        artifact = ReasonArtifact.from_dict(d)
        assert artifact.uri == d["uri"]

    def test_roundtrip_preserves_pattern(self):
        d = self._sample_dict()
        artifact = ReasonArtifact.from_dict(d)
        assert artifact.pattern == d["pattern"]

    def test_roundtrip_preserves_score(self):
        d = self._sample_dict()
        artifact = ReasonArtifact.from_dict(d)
        assert artifact.score == d["score"]

    def test_roundtrip_preserves_thresholds(self):
        d = self._sample_dict()
        artifact = ReasonArtifact.from_dict(d)
        assert artifact.thresholds.high_confidence == 0.85
        assert artifact.thresholds.moderate_confidence == 0.65
        assert artifact.thresholds.minimum_signal == 0.45

    def test_roundtrip_preserves_provenance(self):
        d = self._sample_dict()
        artifact = ReasonArtifact.from_dict(d)
        assert artifact.provenance.agent_id == "agent-0"
        assert artifact.provenance.arbitration_event_id == "evt-abc123"
        assert artifact.provenance.audit_hash == "d" * 64

    def test_roundtrip_preserves_metadata(self):
        d = self._sample_dict()
        artifact = ReasonArtifact.from_dict(d)
        assert artifact.metadata.evidence_count == 92000
        assert artifact.metadata.domain == "finance"

    def test_version_defaults_to_1(self):
        d = self._sample_dict()
        del d["metadata"]["version"]
        artifact = ReasonArtifact.from_dict(d)
        assert artifact.metadata.version == 1


# ---------------------------------------------------------------------------
# ArtifactThresholds.classify — all 4 tiers
# ---------------------------------------------------------------------------

class TestClassify:
    def setup_method(self):
        self.t = ArtifactThresholds(
            high_confidence=0.85,
            moderate_confidence=0.65,
            minimum_signal=0.45,
        )

    def test_high_confidence(self):
        assert self.t.classify(0.90) == "high_confidence"
        assert self.t.classify(0.85) == "high_confidence"

    def test_moderate_confidence(self):
        assert self.t.classify(0.80) == "moderate_confidence"
        assert self.t.classify(0.65) == "moderate_confidence"

    def test_minimum_signal(self):
        assert self.t.classify(0.60) == "minimum_signal"
        assert self.t.classify(0.45) == "minimum_signal"

    def test_no_signal(self):
        assert self.t.classify(0.40) == "no_signal"
        assert self.t.classify(0.0) == "no_signal"
        assert self.t.classify(-1.0) == "no_signal"


# ---------------------------------------------------------------------------
# compare() — cosine similarity
# ---------------------------------------------------------------------------

class TestCompare:
    def setup_method(self):
        self.client = ReasonClient.__new__(ReasonClient)

    def test_identical_vectors(self):
        artifact = _make_artifact(pattern=[1.0, 0.0, 0.0])
        result = self.client.compare([1.0, 0.0, 0.0], artifact)
        assert abs(result - 1.0) < 1e-9

    def test_orthogonal_vectors(self):
        artifact = _make_artifact(pattern=[1.0, 0.0, 0.0])
        result = self.client.compare([0.0, 1.0, 0.0], artifact)
        assert abs(result - 0.0) < 1e-9

    def test_opposite_vectors(self):
        artifact = _make_artifact(pattern=[1.0, 0.0, 0.0])
        result = self.client.compare([-1.0, 0.0, 0.0], artifact)
        assert abs(result - (-1.0)) < 1e-9

    def test_known_45_degree_similarity(self):
        # [1, 1] vs [1, 0] → cos(45°) = 1/sqrt(2) ≈ 0.7071
        artifact = _make_artifact(pattern=[1.0, 0.0])
        result = self.client.compare([1.0, 1.0], artifact)
        assert abs(result - (1.0 / math.sqrt(2))) < 1e-9

    def test_scaled_vectors_same_direction(self):
        # Scaling should not change cosine similarity
        artifact = _make_artifact(pattern=[2.0, 4.0, 6.0])
        result = self.client.compare([1.0, 2.0, 3.0], artifact)
        assert abs(result - 1.0) < 1e-9

    def test_zero_feature_vector_returns_zero(self):
        artifact = _make_artifact(pattern=[1.0, 2.0, 3.0])
        result = self.client.compare([0.0, 0.0, 0.0], artifact)
        assert result == 0.0

    def test_zero_pattern_returns_zero(self):
        artifact = _make_artifact(pattern=[0.0, 0.0, 0.0])
        result = self.client.compare([1.0, 2.0, 3.0], artifact)
        assert result == 0.0


# ---------------------------------------------------------------------------
# Audit hash format — bare 64-char hex
# ---------------------------------------------------------------------------

class TestAuditHashFormat:
    def test_audit_hash_is_bare_hex(self):
        # Verified: app.py stores bare hex (no "sha256:" prefix)
        audit_hash = "a3f2" * 16  # 64-char hex string
        assert len(audit_hash) == 64
        artifact = _make_artifact(audit_hash=audit_hash)
        assert artifact.provenance.audit_hash == audit_hash
        assert not artifact.provenance.audit_hash.startswith("sha256:")

    def test_audit_hash_length(self):
        import hashlib
        # SHA-256 produces 64 hex chars (32 bytes × 2)
        sample = hashlib.sha256(b"test").hexdigest()
        assert len(sample) == 64
        artifact = _make_artifact(audit_hash=sample)
        assert len(artifact.provenance.audit_hash) == 64
