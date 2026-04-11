"""
End-to-end tests for the reason:// protocol against a live Xport node.

Run with:
    pytest sdk/reason_py/tests/test_e2e.py -m e2e -v

These tests require a live Xport node. Set REASON_E2E_ENDPOINT to override
the default (https://reason.astrognosy.com). Tests are automatically skipped
if the node is unreachable.

All tests are read-only — no write access or API key required.
"""
from __future__ import annotations

import math
import os
import sys
import urllib.request
import urllib.error

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reason_py.client import ReasonClient, ReasonResolutionError, ReasonURIError
from reason_py.models import ReasonArtifact


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ENDPOINT = os.environ.get("REASON_E2E_ENDPOINT", "https://reason.astrognosy.com")

# Known seeded URIs (from seed.py bootstrap)
FINANCE_URI = "reason://finance/fraud/anomaly-detection"
CYBER_URI = "reason://cybersecurity/network/port-scan-classification"
MEDICINE_URI = "reason://medicine/records/longitudinal-maintenance-prediction"

# Finance fraud feature vectors (from finance_example.py's extract_features())
# [amount_normalized, velocity_score, geo_deviation, time_of_day_score,
#  merchant_risk_score, device_fingerprint_score]
FRAUD_VECTORS = [
    [0.92, 0.87, 0.95, 0.78, 0.91, 0.88],   # TXN-8821 — high fraud signal
    [0.89, 0.78, 0.91, 0.82, 0.85, 0.76],   # TXN-9034 — high fraud signal
    [0.94, 0.91, 0.89, 0.85, 0.93, 0.90],   # TXN-5577 — high fraud signal
]
LEGIT_VECTORS = [
    [0.21, 0.15, 0.08, 0.62, 0.18, 0.24],   # TXN-4412 — low fraud signal
    [0.18, 0.22, 0.11, 0.58, 0.14, 0.19],   # TXN-2201 — low fraud signal
    [0.25, 0.19, 0.14, 0.55, 0.21, 0.27],   # TXN-3309 — low fraud signal
]


# ---------------------------------------------------------------------------
# Pytest marks and skip logic
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.e2e


def _node_reachable() -> bool:
    try:
        with urllib.request.urlopen(f"{ENDPOINT}/health", timeout=5):
            return True
    except Exception:
        return False


# Skip entire module if node is unreachable
if not _node_reachable():
    pytest.skip(
        f"Xport node not reachable at {ENDPOINT} — skipping E2E tests. "
        "Set REASON_E2E_ENDPOINT to override.",
        allow_module_level=True,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    return ReasonClient(endpoint=ENDPOINT)


@pytest.fixture(scope="module")
def finance_artifact(client):
    return client.resolve(FINANCE_URI)


@pytest.fixture(scope="module")
def cyber_artifact(client):
    return client.resolve(CYBER_URI)


@pytest.fixture(scope="module")
def medicine_artifact(client):
    return client.resolve(MEDICINE_URI)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_node_healthy(self):
        import json
        with urllib.request.urlopen(f"{ENDPOINT}/health", timeout=10) as resp:
            body = json.loads(resp.read().decode())
        assert body["status"] == "ok"
        assert body["artifact_count"] >= 3

    def test_node_has_seeded_artifacts(self):
        import json
        with urllib.request.urlopen(f"{ENDPOINT}/health", timeout=10) as resp:
            body = json.loads(resp.read().decode())
        assert body["artifact_count"] >= 3, (
            "Node has fewer than 3 artifacts — re-run seed.py to bootstrap."
        )


# ---------------------------------------------------------------------------
# Resolve — seeded artifacts exist and are well-formed
# ---------------------------------------------------------------------------

class TestResolveSeededArtifacts:
    def test_resolve_finance_artifact(self, finance_artifact):
        assert isinstance(finance_artifact, ReasonArtifact)
        assert finance_artifact.uri == FINANCE_URI

    def test_resolve_cyber_artifact(self, cyber_artifact):
        assert isinstance(cyber_artifact, ReasonArtifact)
        assert cyber_artifact.uri == CYBER_URI

    def test_resolve_medicine_artifact(self, medicine_artifact):
        assert isinstance(medicine_artifact, ReasonArtifact)
        assert medicine_artifact.uri == MEDICINE_URI

    def test_finance_pattern_is_6_dim(self, finance_artifact):
        assert len(finance_artifact.pattern) == 6, (
            f"Finance pattern should be 6-dim, got {len(finance_artifact.pattern)}"
        )

    def test_finance_pattern_is_unit_norm(self, finance_artifact):
        norm = math.sqrt(sum(x * x for x in finance_artifact.pattern))
        assert abs(norm - 1.0) < 1e-3, f"Pattern should be unit-normalized, norm={norm:.6f}"

    def test_all_scores_are_normalized(self, finance_artifact, cyber_artifact, medicine_artifact):
        for art in (finance_artifact, cyber_artifact, medicine_artifact):
            assert 0.0 <= art.score <= 1.0, (
                f"Score {art.score} for {art.uri} is outside [0, 1] — broker normalization bug"
            )

    def test_all_scores_above_threshold(self, finance_artifact, cyber_artifact, medicine_artifact):
        for art in (finance_artifact, cyber_artifact, medicine_artifact):
            assert art.score >= 0.5, (
                f"Score {art.score} for {art.uri} is below deposit threshold (0.5)"
            )

    def test_finance_thresholds_present(self, finance_artifact):
        t = finance_artifact.thresholds
        assert t.high_confidence > t.moderate_confidence > t.minimum_signal
        assert t.minimum_signal > 0.0

    def test_provenance_has_audit_hash(self, finance_artifact):
        h = finance_artifact.provenance.audit_hash
        assert len(h) == 64
        assert not h.startswith("sha256:")
        int(h, 16)  # must be valid hex

    def test_evidence_count_is_positive(self, finance_artifact):
        assert finance_artifact.metadata.evidence_count > 0

    def test_finance_evidence_count(self, finance_artifact):
        assert finance_artifact.metadata.evidence_count == 92000

    def test_metadata_domain_matches_uri(self, finance_artifact):
        assert finance_artifact.metadata.domain == "finance"

    def test_metadata_category_matches_uri(self, finance_artifact):
        assert finance_artifact.metadata.category == "fraud"

    def test_metadata_task_matches_uri(self, finance_artifact):
        assert finance_artifact.metadata.task == "anomaly-detection"


# ---------------------------------------------------------------------------
# Resolve — error cases
# ---------------------------------------------------------------------------

class TestResolveErrors:
    def test_resolve_unknown_uri_raises_404(self, client):
        with pytest.raises(ReasonResolutionError):
            client.resolve("reason://unknown/does/not-exist")

    def test_resolve_invalid_uri_raises_uri_error(self, client):
        with pytest.raises(ReasonURIError):
            client.resolve("http://not-a-reason-uri")

    def test_resolve_invalid_segment_raises_uri_error(self, client):
        with pytest.raises(ReasonURIError):
            client.resolve("reason://UPPERCASE/fraud/detection")


# ---------------------------------------------------------------------------
# Compare — cosine similarity on live artifact
# ---------------------------------------------------------------------------

class TestCompare:
    def test_fraud_vectors_score_above_high_confidence(self, client, finance_artifact):
        for vec in FRAUD_VECTORS:
            similarity = client.compare(vec, finance_artifact)
            assert similarity >= finance_artifact.thresholds.high_confidence, (
                f"Fraud vector similarity {similarity:.3f} < "
                f"high_confidence {finance_artifact.thresholds.high_confidence}"
            )

    def test_legit_vectors_score_below_fraud_vectors(self, client, finance_artifact):
        fraud_sims = [client.compare(v, finance_artifact) for v in FRAUD_VECTORS]
        legit_sims = [client.compare(v, finance_artifact) for v in LEGIT_VECTORS]
        assert min(fraud_sims) > max(legit_sims), (
            f"Weakest fraud {min(fraud_sims):.3f} should beat strongest legit {max(legit_sims):.3f}"
        )

    def test_compare_returns_value_in_0_1(self, client, finance_artifact):
        vec = FRAUD_VECTORS[0]
        similarity = client.compare(vec, finance_artifact)
        assert 0.0 <= similarity <= 1.0

    def test_compare_zero_vector_returns_zero(self, client, finance_artifact):
        similarity = client.compare([0.0] * 6, finance_artifact)
        assert similarity == 0.0

    def test_compare_identical_to_pattern_returns_1(self, client, finance_artifact):
        pattern = finance_artifact.pattern
        similarity = client.compare(pattern, finance_artifact)
        assert abs(similarity - 1.0) < 1e-6

    def test_compare_symmetric(self, client, finance_artifact):
        """compare(a, artifact) with artifact.pattern = a should equal 1.0."""
        from reason_py.models import ReasonArtifact, ArtifactThresholds, ArtifactProvenance, ArtifactMetadata
        vec = FRAUD_VECTORS[0]
        # Construct a synthetic artifact with vec as its pattern
        synthetic = ReasonArtifact(
            uri=FINANCE_URI,
            pattern=vec,
            thresholds=finance_artifact.thresholds,
            score=0.9,
            provenance=finance_artifact.provenance,
            metadata=finance_artifact.metadata,
        )
        assert client.compare(vec, synthetic) == pytest.approx(1.0, abs=1e-6)


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

class TestAudit:
    def test_audit_record_retrievable(self, client, finance_artifact):
        artifact_id = finance_artifact.provenance.arbitration_event_id
        import json, urllib.request
        with urllib.request.urlopen(
            f"{ENDPOINT}/audit/{artifact_id}", timeout=10
        ) as resp:
            body = json.loads(resp.read().decode())
        assert body["artifact_id"] == artifact_id
        assert len(body["audit_hash"]) == 64

    def test_audit_hash_matches_provenance(self, client, finance_artifact):
        artifact_id = finance_artifact.provenance.arbitration_event_id
        import json, urllib.request
        with urllib.request.urlopen(
            f"{ENDPOINT}/audit/{artifact_id}", timeout=10
        ) as resp:
            body = json.loads(resp.read().decode())
        assert body["audit_hash"] == finance_artifact.provenance.audit_hash


# ---------------------------------------------------------------------------
# End-to-end fraud detection flow (mirrors finance_example.py)
# ---------------------------------------------------------------------------

class TestFraudDetectionFlow:
    def test_3_of_3_frauds_caught(self, client):
        """Full walkthrough: resolve → compare → classify. No data crosses boundary."""
        artifact = client.resolve(FINANCE_URI)

        # Classify fraud vectors
        for vec in FRAUD_VECTORS:
            sim = client.compare(vec, artifact)
            assert sim >= artifact.thresholds.moderate_confidence, (
                f"Known fraud vector scored {sim:.3f} — below moderate_confidence threshold"
            )

        # Classify legit vectors — should score meaningfully lower than frauds
        legit_sims = [client.compare(v, artifact) for v in LEGIT_VECTORS]
        fraud_sims = [client.compare(v, artifact) for v in FRAUD_VECTORS]
        assert min(fraud_sims) > max(legit_sims), "Fraud/legit separation failed"

    def test_single_api_call_resolves_artifact(self):
        """Verify one HTTP call suffices — resolve is the only network operation."""
        import json, urllib.request
        with urllib.request.urlopen(
            f"{ENDPOINT}/resolve?address=reason://finance/fraud/anomaly-detection",
            timeout=10,
        ) as resp:
            body = json.loads(resp.read().decode())
        assert "pattern" in body
        assert "thresholds" in body
        assert "provenance" in body
