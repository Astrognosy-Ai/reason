"""
reason:// Reference Node — Xport

Reference implementation of a reason:// registry node.
Stores validated reasoning artifacts, resolves reason:// URIs,
and gates entry via WARF arbitration.

Endpoints:
  GET  /health                     — node health + artifact count
  GET  /resolve?address=reason://  — resolve a reason:// URI to its artifact
  GET  /artifacts                  — list all registered artifacts
  GET  /audit/{artifact_id}        — SHA-256 audit record for an artifact
  POST /register                   — submit an artifact for WARF arbitration
                                     (deposits on win, rejects on loss)

Usage:
  uvicorn app:app --host 0.0.0.0 --port 8080

Environment:
  WARF_BROKER_URL   — WARF broker endpoint for arbitration scoring
                      (default: https://warf-broker.up.railway.app)
  DATABASE_URL      — PostgreSQL connection string (Railway Postgres addon format:
                      postgresql://user:pass@host:5432/db). When set, psycopg2 is
                      used with a connection pool. When unset, falls back to SQLite.
  NODE_DB           — SQLite DB path (default: registry.db). Ignored when DATABASE_URL
                      is set. Accepts :memory: for tests.
  NODE_ID           — identifier for this node (default: reason-ref-node-0)
  XPORT_API_KEY     — secret key required in X-API-Key header for POST /register
                      (leave unset to disable auth in local dev; always set in prod)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.request
import uuid
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

# ─── Config ───────────────────────────────────────────────────────────────────

WARF_BROKER_URL = os.environ.get(
    "WARF_BROKER_URL", "https://warf-broker.up.railway.app"
).rstrip("/")
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DB_PATH = os.environ.get("NODE_DB", "registry.db")
NODE_ID = os.environ.get("NODE_ID", "reason-ref-node-0")

# API key for write endpoints — set XPORT_API_KEY env var to enable auth.
# If unset, /register is open (useful for local dev only — always set in prod).
XPORT_API_KEY = os.environ.get("XPORT_API_KEY", "")

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str = Security(_api_key_header)) -> None:
    """Dependency: reject requests with a missing or wrong API key (when auth is enabled)."""
    if not XPORT_API_KEY:
        return  # auth disabled — dev/local mode
    if key != XPORT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header.")

REASON_URI_PATTERN = re.compile(
    r"^reason://([a-z][a-z0-9-]{1,62})/([a-z][a-z0-9-]{1,62})/([a-z][a-z0-9-]{1,62})$"
)

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="reason:// Reference Node",
    description=(
        "Reference Xport node for the reason:// protocol. "
        "Artifacts enter only by winning WARF arbitration. "
        "Resolution is one line. No raw data ever stored."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_start_time = time.time()


# ─── Database ─────────────────────────────────────────────────────────────────

_pg_pool = None  # psycopg2 connection pool; None when using SQLite


def _init_pg_pool() -> None:
    """Initialize the psycopg2 connection pool. Called once at startup."""
    global _pg_pool
    import psycopg2.pool  # type: ignore[import]
    _pg_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL)


class _DB:
    """
    Thin adapter providing a uniform interface over sqlite3 and psycopg2.

    Both backends support row["column_name"] access (sqlite3.Row and
    RealDictCursor behave identically for this purpose). The adapter
    handles placeholder translation (? → %s) and connection lifecycle.
    """

    def __init__(self, backend: str, conn: Any) -> None:
        self._backend = backend
        self._conn = conn
        if backend == "pg":
            import psycopg2.extras  # type: ignore[import]
            self._cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            self._cur = None

    def execute(self, sql: str, params: tuple = ()) -> Any:
        if self._backend == "pg":
            self._cur.execute(sql.replace("?", "%s"), params)
            return self._cur
        return self._conn.execute(sql, params)

    def upsert_artifact(
        self, artifact_id: str, address: str, domain: str, category: str, task: str,
        pattern_json: str, thresholds_json: str, score: float, n_examples: int,
        agent_id: str, deposited_at: str, audit_hash: str, metadata_json: str,
    ) -> None:
        """Insert or replace an artifact. Handles SQLite vs PostgreSQL syntax."""
        params = (
            artifact_id, address, domain, category, task,
            pattern_json, thresholds_json, score, n_examples,
            agent_id, deposited_at, audit_hash, metadata_json,
        )
        if self._backend == "pg":
            self._cur.execute("""
                INSERT INTO artifacts
                    (artifact_id, address, domain, category, task,
                     pattern_json, thresholds_json, score, n_examples,
                     agent_id, deposited_at, audit_hash, metadata_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (address) DO UPDATE SET
                    artifact_id = EXCLUDED.artifact_id,
                    domain = EXCLUDED.domain,
                    category = EXCLUDED.category,
                    task = EXCLUDED.task,
                    pattern_json = EXCLUDED.pattern_json,
                    thresholds_json = EXCLUDED.thresholds_json,
                    score = EXCLUDED.score,
                    n_examples = EXCLUDED.n_examples,
                    agent_id = EXCLUDED.agent_id,
                    deposited_at = EXCLUDED.deposited_at,
                    audit_hash = EXCLUDED.audit_hash,
                    metadata_json = EXCLUDED.metadata_json
            """, params)
        else:
            self._conn.execute("""
                INSERT OR REPLACE INTO artifacts
                    (artifact_id, address, domain, category, task,
                     pattern_json, thresholds_json, score, n_examples,
                     agent_id, deposited_at, audit_hash, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, params)

    def commit(self) -> None:
        self._conn.commit()

    def close(self) -> None:
        if self._backend == "pg":
            self._conn.commit()
            _pg_pool.putconn(self._conn)
        else:
            self._conn.close()


def get_db() -> _DB:
    if DATABASE_URL:
        import psycopg2  # type: ignore[import]
        conn = _pg_pool.getconn()
        return _DB("pg", conn)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return _DB("sqlite", conn)


_SCHEMA_CREATE = """
    CREATE TABLE IF NOT EXISTS artifacts (
        artifact_id   TEXT PRIMARY KEY,
        address       TEXT NOT NULL UNIQUE,
        domain        TEXT NOT NULL,
        category      TEXT NOT NULL,
        task          TEXT NOT NULL,
        pattern_json  TEXT NOT NULL,
        thresholds_json TEXT NOT NULL,
        score         REAL NOT NULL,
        n_examples    INTEGER NOT NULL,
        agent_id      TEXT NOT NULL,
        deposited_at  TEXT NOT NULL,
        audit_hash    TEXT NOT NULL,
        metadata_json TEXT NOT NULL DEFAULT '{}'
    )
"""
_SCHEMA_INDEX = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_artifacts_address ON artifacts(address)
"""


def init_db() -> None:
    db = get_db()
    if db._backend == "pg":
        db._cur.execute(_SCHEMA_CREATE)
        db._cur.execute(_SCHEMA_INDEX)
    else:
        db._conn.executescript(_SCHEMA_CREATE + ";" + _SCHEMA_INDEX + ";")
    db.commit()
    db.close()


# ─── Models ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    address: str                        # reason://domain/category/task
    pattern: List[float]                # structural centroid — non-invertible
    thresholds: Dict[str, float]        # {"high_confidence": 0.85, ...}
    n_examples: int                     # evidence base size
    agent_id: str                       # submitting agent identifier
    task_description: str               # natural language description for arbitration
    metadata: Dict[str, Any] = {}       # public, non-sensitive only


class ArtifactOut(BaseModel):
    artifact_id: str
    address: str
    pattern: List[float]
    thresholds: Dict[str, float]
    score: float
    n_examples: int
    agent_id: str
    deposited_at: str
    audit_hash: str
    metadata: Dict[str, Any]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _validate_uri(address: str) -> None:
    if not REASON_URI_PATTERN.match(address):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid reason:// URI: {address!r}. "
                "Format: reason://<domain>/<category>/<task> "
                "(lowercase letters, digits, hyphens only)"
            ),
        )


def _compute_audit_hash(artifact_id: str, address: str, score: float,
                         agent_id: str, timestamp: str) -> str:
    payload = f"{artifact_id}|{address}|{score:.6f}|{agent_id}|{timestamp}"
    return hashlib.sha256(payload.encode()).hexdigest()


def _to_reason_artifact_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Serialize a DB row to the ReasonArtifact wire format expected by the SDK."""
    return {
        "uri": row["address"],
        "pattern": json.loads(row["pattern_json"]),
        "thresholds": json.loads(row["thresholds_json"]),
        "score": row["score"],
        "provenance": {
            "agent_id": row["agent_id"],
            "deposited_at": row["deposited_at"],
            "arbitration_event_id": row["artifact_id"],
            "audit_hash": row["audit_hash"],
        },
        "metadata": {
            **json.loads(row["metadata_json"]),
            "evidence_count": row["n_examples"],
            "domain": row["domain"],
            "category": row["category"],
            "task": row["task"],
        },
    }


def _call_warf_broker(address: str, pattern: List[float],
                       task_description: str, n_examples: int,
                       agent_id: str) -> Dict[str, Any]:
    """
    Call the WARF broker to arbitrate this artifact submission.
    Sends the submission against a null-baseline package. The submission
    must win (score > baseline score) and exceed 0.5 to earn a deposit.

    Returns a normalized dict: {"winning_agent": str, "winning_score": float}.
    """
    payload = json.dumps({
        "query_id": f"reason-reg-{uuid.uuid4().hex[:8]}",
        "query_text": task_description,
        "packages": [
            {
                "agent_id": agent_id,
                "answer_text": address,
                "corpus": [
                    {
                        "doc_id": "pattern-centroid",
                        "text": (
                            f"Structural centroid for {address}. "
                            f"Evidence base: {n_examples} examples. "
                            f"Pattern dimension: {len(pattern)}."
                        ),
                    }
                ],
            },
            {
                "agent_id": "__null_baseline__",
                "answer_text": "null baseline — no structural pattern submitted",
                "corpus": [
                    {
                        "doc_id": "baseline",
                        "text": "No pattern. No evidence. Null hypothesis.",
                    }
                ],
            },
        ],
    }).encode()

    req = urllib.request.Request(
        f"{WARF_BROKER_URL}/arbitrate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read().decode())
            winner = raw.get("winner", {})
            all_scores = raw.get("all_scores", {})
            winning_agent = winner.get("agent_id", "__null_baseline__")
            winning_score = float(winner.get("score", 0.0))
            return {
                "winning_agent": winning_agent,
                "winning_score": winning_score,
                "all_scores": all_scores,
            }
    except urllib.error.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"WARF broker returned {e.code}: {e.read().decode()[:200]}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"WARF broker unreachable: {str(e)[:200]}",
        )


def _row_to_artifact(row: sqlite3.Row) -> ArtifactOut:
    return ArtifactOut(
        artifact_id=row["artifact_id"],
        address=row["address"],
        pattern=json.loads(row["pattern_json"]),
        thresholds=json.loads(row["thresholds_json"]),
        score=row["score"],
        n_examples=row["n_examples"],
        agent_id=row["agent_id"],
        deposited_at=row["deposited_at"],
        audit_hash=row["audit_hash"],
        metadata=json.loads(row["metadata_json"]),
    )


# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup() -> None:
    if DATABASE_URL:
        _init_pg_pool()
    init_db()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> Dict[str, Any]:
    db = get_db()
    count = db.execute("SELECT COUNT(*) AS cnt FROM artifacts").fetchone()["cnt"]
    db.close()
    return {
        "status": "ok",
        "node_id": NODE_ID,
        "uptime_seconds": round(time.time() - _start_time, 1),
        "artifact_count": count,
        "warf_broker": WARF_BROKER_URL,
        "protocol": "reason:// v0.1",
    }


@app.get("/resolve")
def resolve(address: str = Query(..., description="reason:// URI")) -> Dict[str, Any]:
    """
    Resolve a reason:// URI to its validated reasoning artifact.

    Example:
        GET /resolve?address=reason://finance/fraud/synthetic-identity-temporal-motif
    """
    _validate_uri(address)
    db = get_db()
    row = db.execute(
        "SELECT * FROM artifacts WHERE address = ?", (address,)
    ).fetchone()
    db.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"No artifact registered at {address!r}. "
                   "Submit via POST /register to initiate arbitration.",
        )

    return _to_reason_artifact_dict(row)


@app.get("/artifacts")
def list_artifacts(
    domain: Optional[str] = None,
    address: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> List[Dict[str, Any]]:
    """List registered artifacts, optionally filtered by domain or exact address."""
    db = get_db()
    if address:
        rows = db.execute(
            "SELECT * FROM artifacts WHERE address = ? ORDER BY deposited_at DESC LIMIT ? OFFSET ?",
            (address, limit, offset),
        ).fetchall()
    elif domain:
        rows = db.execute(
        