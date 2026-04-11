"""
Integration tests for the Xport node (warf-node/app.py).

Uses FastAPI TestClient against the real app with an in-memory SQLite DB.
The WARF broker is mocked via unittest.mock.patch — no second server needed.

Run with:
    pytest sdk/reason_py/tests/test_integration.py

Requirements:
    pip install fastapi httpx pytest
"""

import hashlib
import json
import os
import sys
import unittest.mock
from io import BytesIO

import tempfile

import pytest

# Add warf-node to path so we can import app.py
_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, os.path.join(_REPO_ROOT, "warf-node"))

os.environ["XPORT_API_KEY"] = ""  # disable auth for tests

import app as xport_app  # noqa: E402 — must be after env setup

from fastapi.testclient import TestClient  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _MockResponse:
    """Minimal urllib response mock."""
    def __init__(self, body: dict):
        self._data = json.dumps(body).encode()

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def _broker_mock(score: float, agent_id: str = "test-agent-0"):
    """Return a context manager that patches urllib.request.urlopen with a fixed broker result."""
    return unittest.mock.patch(
        "urllib.request.urlopen",
        return_value=_MockResponse({
            "winner": {"agent_id": agent_id, "score": score},
            "winning_score": score,
            "winning_agent": agent_id,
        }),
    )


def _sample_register_payload(address="reason://finance/fraud/anomaly-detection"):
    return {
        "address": address,
        "pattern": [0.1, 0.2, 0.3, 0.4, 0.5],
        "thresholds": {
            "high_confidence": 0.85,
            "moderate_confidence": 0.65,
            "minimum_signal": 0.45,
        },
        "n_examples": 92000,
        "agent_id": "test-agent-0",
        "task_description": "Fraud anomaly detection pattern from labeled transaction data.",
        "metadata": {
            "domain": "finance",
            "category": "fraud",
            "task": "anomaly-detection",
            "version": 1,
        },
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Fresh TestClient with a clean temp-file SQLite DB for each test.

    SQLite :memory: creates a new empty DB per connection, so each sqlite3.connect()
    call would see a different database. A real temp file avoids this.
    """
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    xport_app.DB_PATH = db_path
    xport_app.init_db()
    with TestClient(xport_app.app) as c:
        yield c
    os.unlink(db_path)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert "artifact_count" in body
        assert "node_id" in body

    def test_health_artifact_count_starts_at_zero(self, client):
        resp = client.get("/health")
        assert resp.json()["artifact_count"] == 0


# ---------------------------------------------------------------------------
# GET /resolve — missing address
# ---------------------------------------------------------------------------

class TestResolveNotFound:
    def test_resolve_missing_returns_404(self, client):
        resp = client.get("/resolve", params={"address": "reason://finance/fraud/anomaly-detection"})
        assert resp.status_code == 404

    def test_resolve_invalid_uri_returns_400(self, client):
        resp = client.get("/resolve", params={"address": "http://not-a-reason-uri"})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# POST /register — deposited (score=0.75)
# ---------------------------------------------------------------------------

class TestRegisterDeposit:
    def test_register_accepted_returns_201(self, client):
        with _broker_mock(score=0.75):
            resp = client.post("/register", json=_sample_register_payload())
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "deposited"
        assert body["score"] == 0.75
        assert "artifact_id" in body
        assert "audit_hash" in body

    def test_register_accepted_health_count_increments(self, client):
        with _broker_mock(score=0.75):
            client.post("/register", json=_sample_register_payload())
        resp = client.get("/health")
        assert resp.json()["artifact_count"] == 1

    def test_audit_hash_is_bare_hex(self, client):
        with _broker_mock(score=0.75):
            resp = client.post("/register", json=_sample_register_payload())
        audit_hash = resp.json()["audit_hash"]
        assert len(audit_hash) == 64
        assert not audit_hash.startswith("sha256:")
        # Must be valid hex
        int(audit_hash, 16)

    def test_audit_hash_is_verifiable(self, client):
        """Verify the audit hash matches the documented formula."""
        with _broker_mock(score=0.75):
            resp = client.post("/register", json=_sample_register_payload())
        body = resp.json()
        artifact_id = body["artifact_id"]
        address = body["address"]
        score = body["score"]
        deposited_at = body["deposited_at"]
        agent_id = _sample_register_payload()["agent_id"]

        expected = hashlib.sha256(
            f"{artifact_id}|{address}|{score:.6f}|{agent_id}|{deposited_at}".encode()
        ).hexdigest()
        assert body["audit_hash"] == expected


# ---------------------------------------------------------------------------
# GET /resolve — after deposit
# ---------------------------------------------------------------------------

class TestResolveAfterDeposit:
    def test_resolve_returns_artifact_after_deposit(self, client):
        address = "reason://finance/fraud/anomaly-detection"
        with _broker_mock(score=0.75):
            client.post("/register", json=_sample_register_payload(address))

        resp = client.get("/resolve", params={"address": address})
        assert resp.status_code == 200
        body = resp.json()
        assert body["uri"] == address
        assert body["pattern"] == _sample_register_payload()["pattern"]
        assert body["score"] == 0.75

    def test_resolved_artifact_has_bare_hex_audit_hash(self, client):
        address = "reason://finance/fraud/anomaly-detection"
        with _broker_mock(score=0.75):
            client.post("/register", json=_sample_register_payload(address))

        resp = client.get("/resolve", params={"address": address})
        audit_hash = resp.json()["provenance"]["audit_hash"]
        assert len(audit_hash) == 64
        assert not audit_hash.startswith("sha256:")


# ---------------------------------------------------------------------------
# GET /audit/{id}
# ---------------------------------------------------------------------------

class TestAudit:
    def test_audit_record_verifiable(self, client):
        with _broker_mock(score=0.75):
            reg = client.post("/register", json=_sample_register_payload())
        artifact_id = reg.json()["artifact_id"]

        resp = client.get(f"/audit/{artifact_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert "audit_hash" in body
        assert "verify" in body
        assert len(body["audit_hash"]) == 64

    def test_audit_missing_returns_404(self, client):
        resp = client.get("/audit/nonexistent-id")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /register — rejected (score=0.3)
# ---------------------------------------------------------------------------

class TestRegisterRejected:
    def test_register_rejected_when_score_below_threshold(self, client):
        with _broker_mock(score=0.3):
            resp = client.post("/register", json=_sample_register_payload())
        # Node returns 201 with rejected status (not a 4xx — the request was valid,
        # arbitration just didn't award a deposit)
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "rejected"
        assert body["score"] == 0.3

    def test_rejected_artifact_not_stored(self, client):
        with _broker_mock(score=0.3):
            client.post("/register", json=_sample_register_payload())
        resp = client.get("/health")
        assert resp.json()["artifact_count"] == 0

    def test_rejected_when_null_baseline_wins(self, client):
        # Submitter scored above 0.5 but the null baseline won — still rejected
        with _broker_mock(score=0.6, agent_id="__null_baseline__"):
            resp = client.post("/register", json=_sample_register_payload())
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "rejected"
        assert "null baseline" in body["reason"]
