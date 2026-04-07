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
  POST /promote                    — deposit a pre-scored artifact from Xtend
                                     (skips arbitration, scoring done upstream)

Usage:
  uvicorn app:app --host 0.0.0.0 --port 8080

Environment:
  DATABASE_URL      — Postgres connection string (preferred).
                      If set, uses Postgres. If unset, falls back to SQLite (dev only).
  WARF_BROKER_URL   — WARF broker endpoint for arbitration scoring
                      (default: https://warf-broker.up.railway.app)
  NODE_DB           — path to SQLite database when DATABASE_URL is unset (default: registry.db)
  NODE_ID           — identifier for this node (default: reason-ref-node-0)
  XPORT_API_KEY     — secret key required in X-API-Key header for write endpoints.
                      Leave unset to disable auth in local dev; always set in prod.
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

DATABASE_URL = os.environ.get("DATABASE_URL", "")
WARF_BROKER_URL = os.environ.get(
    "WARF_BROKER_URL", "https://warf-broker.up.railway.app"
).rstrip("/")
DB_PATH = os.environ.get("NODE_DB", "registry.db")
NODE_ID = os.environ.get("NODE_ID", "reason-ref-node-0")

# API key for write endpoints — set XPORT_API_KEY env var to enable auth.
# If unset, /register and /promote are open (dev/local only — always set in prod).
XPORT_API_KEY = os.environ.get("XPORT_API_KEY", "")

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str = Security(_api_key_header)) -> None:
    """Dependency: reject requests with a missing or wrong API key (when auth is enabled)."""
    if not XPORT_API_KEY:
        return  # auth disabled — dev/local mode
    if key != XPORT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header.")


REASON_URI_PATTERN = re.compile(
    r"^reason://([a-z][a-z0-9\-]*)/([a-z][a-z0-9\-]*)/([a-z][a-z0-9\-]*)$"
)

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="reason:// Reference Node",
    description=(
        "Reference Xport node for the reason:// protocol. "
        "Artifacts enter only by winning WARF arbitration. "
        "Resolution is one line. No raw data ever stored."
    ),
    version="0.2.0",
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

def _is_postgres() -> bool:
    return DATABASE_URL.startswith("postgres")


def _ph() -> str:
    """Return the correct SQL placeholder for the active backend."""
    return "%s" if _is_postgres() else "?"


def get_db():
    """Return an open database connection for the active backend."""
    if _is_postgres():
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _exec(conn, sql: str, params=()):
    """Execute SQL on either backend, returning a cursor with dict-style row access."""
    if _is_postgres():
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        return cur
    return conn.execute(sql, params)


def _upsert_artifact_sql() -> str:
    """
    Return the correct INSERT-or-replace SQL for the active backend.

    Postgres uses INSERT ... ON CONFLICT (address) DO UPDATE SET ...
    SQLite uses INSERT OR REPLACE INTO ...

    The column list and parameter tuple are identical for both — 13 values in order:
    artifact_id, address, domain, category, task, pattern_json, thresholds_json,
    score, n_examples, agent_id, deposited_at, audit_hash, metadata_json
    """
    p = _ph()
    cols = (
        "artifact_id, address, domain, category, task, "
        "pattern_json, thresholds_json, score, n_examples, "
        "agent_id, deposited_at, audit_hash, metadata_json"
    )
    vals = ", ".join([p] * 13)

    if _is_postgres():
        return f"""
            INSERT INTO artifacts ({cols})
            VALUES ({vals})
            ON CONFLICT (address) DO UPDATE SET
                artifact_id     = EXCLUDED.artifact_id,
                domain          = EXCLUDED.domain,
                category        = EXCLUDED.category,
                task            = EXCLUDED.task,
                pattern_json    = EXCLUDED.pattern_json,
                thresholds_json = EXCLUDED.thresholds_json,
                score           = EXCLUDED.score,
                n_examples      = EXCLUDED.n_examples,
                agent_id        = EXCLUDED.agent_id,
                deposited_at    = EXCLUDED.deposited_at,
                audit_hash      = EXCLUDED.audit_hash,
                metadata_json   = EXCLUDED.metadata_json
        """
    return f"INSERT OR REPLACE INTO artifacts ({cols}) VALUES ({vals})"


def init_db() -> None:
    conn = get_db()

    if _is_postgres():
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id     TEXT PRIMARY KEY,
                address         TEXT NOT NULL UNIQUE,
                domain          TEXT NOT NULL,
                category        TEXT NOT NULL,
                task            TEXT NOT NULL,
                pattern_json    TEXT NOT NULL,
                thresholds_json TEXT NOT NULL,
                score           REAL NOT NULL,
                n_examples      INTEGER NOT NULL,
                agent_id        TEXT NOT NULL,
                deposited_at    TEXT NOT NULL,
                audit_hash      TEXT NOT NULL,
                metadata_json   TEXT NOT NULL DEFAULT '{}'
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    else:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id     TEXT PRIMARY KEY,
                address         TEXT NOT NULL UNIQUE,
                domain          TEXT NOT NULL,
                category        TEXT NOT NULL,
                task            TEXT NOT NULL,
                pattern_json    TEXT NOT NULL,
                thresholds_json TEXT NOT NULL,
                score           REAL NOT NULL,
                n_examples      INTEGER NOT NULL,
                agent_id        TEXT NOT NULL,
                deposited_at    TEXT NOT NULL,
                audit_hash      TEXT NOT NULL,
                metadata_json   TEXT NOT NULL DEFAULT '{}'
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_artifacts_address
                ON artifacts(address);
        """)
        conn.commit()
        conn.close()


# ─── Models ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    address: str                        # reason://domain/category/task
    pattern: List[float]                # structural centroid — non-invertible
    thresholds: Dict[str, float]        # {"high_confidence": 0.85, ...}
    n_examples: int                     # evidence base size
    agent_id: str                       # submitting agent identifier
    task_description: str               # natural language description for arbitration
    metadata: Dict[str, Any] = {}       # public, non-sensitive only


class PromoteRequest(BaseModel):
    address: str                        # reason://domain/category/task
    flow_type: str                      # "Xfer", "Xact", or "Xchange"
    payload: Dict[str, Any]             # winning artifact payload
    pcf_score: float                    # pre-computed score from Xtend
    balmathic_kappa: float              # κ exponent from Xtend
    agent_id: str                       # winning agent identifier
    audit_hash: str                     # audit hash from Xtend scoring
    metadata: Dict[str, Any] = {}


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


def _to_reason_artifact_dict(row) -> Dict[str, Any]:
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


def _row_to_artifact(row) -> ArtifactOut:
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
    init_db()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> Dict[str, Any]:
    db = get_db()
    row = _exec(db, "SELECT COUNT(*) AS cnt FROM artifacts").fetchone()
    count = row["cnt"]
    db.close()
    return {
        "status": "ok",
        "node_id": NODE_ID,
        "uptime_seconds": round(time.time() - _start_time, 1),
        "artifact_count": count,
        "warf_broker": WARF_BROKER_URL,
        "backend": "postgres" if _is_postgres() else "sqlite",
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
    row = _exec(
        db,
        f"SELECT * FROM artifacts WHERE address = {_ph()}",
        (address,),
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
    p = _ph()
    db = get_db()
    if address:
        rows = _exec(
            db,
            f"SELECT * FROM artifacts WHERE address = {p} ORDER BY deposited_at DESC LIMIT {p} OFFSET {p}",
            (address, limit, offset),
        ).fetchall()
    elif domain:
        rows = _exec(
            db,
            f"SELECT * FROM artifacts WHERE domain = {p} ORDER BY deposited_at DESC LIMIT {p} OFFSET {p}",
            (domain, limit, offset),
        ).fetchall()
    else:
        rows = _exec(
            db,
            f"SELECT * FROM artifacts ORDER BY deposited_at DESC LIMIT {p} OFFSET {p}",
            (limit, offset),
        ).fetchall()
    db.close()
    return [_to_reason_artifact_dict(r) for r in rows]


@app.get("/audit/{artifact_id}")
def get_audit(artifact_id: str) -> Dict[str, Any]:
    """
    Retrieve the SHA-256 audit record for a specific artifact.
    Audit hashes are chained — verifiable without trusting this node.
    """
    db = get_db()
    row = _exec(
        db,
        f"""SELECT artifact_id, address, score, agent_id, deposited_at, audit_hash
            FROM artifacts WHERE artifact_id = {_ph()}""",
        (artifact_id,),
    ).fetchone()
    db.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_id!r} not found.")

    return {
        "artifact_id": row["artifact_id"],
        "address": row["address"],
        "score": row["score"],
        "agent_id": row["agent_id"],
        "deposited_at": row["deposited_at"],
        "audit_hash": row["audit_hash"],
        "verify": (
            f"sha256({row['artifact_id']}|{row['address']}|"
            f"{row['score']:.6f}|{row['agent_id']}|{row['deposited_at']})"
        ),
    }


@app.post("/register", status_code=201)
def register(req: RegisterRequest, _: None = Depends(require_api_key)) -> Dict[str, Any]:
    """
    Submit a structural artifact for WARF arbitration.

    The artifact enters the registry ONLY if it wins arbitration.
    Arbitration is conducted by the WARF broker using PCF scoring.
    A score above 0.5 is required for deposit.

    The pattern must be the non-invertible structural centroid of the
    learned reasoning pattern — not raw data, not model weights.
    Raw data fields are architecturally absent from this schema.
    """
    _validate_uri(req.address)

    if len(req.pattern) == 0:
        raise HTTPException(status_code=400, detail="pattern must be non-empty.")
    if req.n_examples < 1:
        raise HTTPException(status_code=400, detail="n_examples must be >= 1.")

    required_threshold_keys = {"high_confidence", "moderate_confidence", "minimum_signal"}
    if not required_threshold_keys.issubset(req.thresholds):
        raise HTTPException(
            status_code=400,
            detail=f"thresholds must include: {sorted(required_threshold_keys)}",
        )

    # Check if this address already has a high-confidence artifact
    db = get_db()
    existing = _exec(
        db,
        f"SELECT score FROM artifacts WHERE address = {_ph()}",
        (req.address,),
    ).fetchone()
    db.close()

    if existing and existing["score"] >= 0.95:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Address {req.address!r} already holds a high-confidence artifact "
                f"(score={existing['score']:.3f}). "
                "Challenger must demonstrate significantly higher evidence quality."
            ),
        )

    # Call WARF broker for arbitration
    broker_result = _call_warf_broker(
        address=req.address,
        pattern=req.pattern,
        task_description=req.task_description,
        n_examples=req.n_examples,
        agent_id=req.agent_id,
    )

    pcf_score = float(broker_result.get("winning_score", 0.0))

    # Score threshold: must earn above 0.5 to deposit
    if pcf_score < 0.5:
        return {
            "status": "rejected",
            "reason": "Arbitration score below deposit threshold (0.5).",
            "score": pcf_score,
            "address": req.address,
        }

    # Submitter must beat the null baseline
    winning_agent = broker_result.get("winning_agent", "__null_baseline__")
    if winning_agent != req.agent_id:
        return {
            "status": "rejected",
            "reason": "Submission did not beat null baseline in arbitration.",
            "score": pcf_score,
            "address": req.address,
        }

    # If existing artifact has higher score, reject challenger
    if existing and existing["score"] >= pcf_score:
        return {
            "status": "rejected",
            "reason": (
                f"Existing artifact score ({existing['score']:.3f}) >= "
                f"challenger score ({pcf_score:.3f}). Incumbent retained."
            ),
            "score": pcf_score,
            "address": req.address,
        }

    # Deposit artifact
    artifact_id = uuid.uuid4().hex
    deposited_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    audit_hash = _compute_audit_hash(
        artifact_id=artifact_id,
        address=req.address,
        score=pcf_score,
        agent_id=req.agent_id,
        timestamp=deposited_at,
    )

    uri_match = REASON_URI_PATTERN.match(req.address)
    domain = req.metadata.get("domain", uri_match.group(1))
    category = req.metadata.get("category", uri_match.group(2))
    task = req.metadata.get("task", uri_match.group(3))

    db = get_db()
    _exec(
        db,
        _upsert_artifact_sql(),
        (
            artifact_id,
            req.address,
            domain,
            category,
            task,
            json.dumps(req.pattern),
            json.dumps(req.thresholds),
            pcf_score,
            req.n_examples,
            req.agent_id,
            deposited_at,
            audit_hash,
            json.dumps(req.metadata),
        ),
    )
    db.commit()
    db.close()

    return {
        "status": "deposited",
        "artifact_id": artifact_id,
        "address": req.address,
        "score": pcf_score,
        "deposited_at": deposited_at,
        "audit_hash": audit_hash,
    }


@app.post("/promote", status_code=201)
def promote(req: PromoteRequest, _: None = Depends(require_api_key)) -> Dict[str, Any]:
    """
    Deposit a pre-scored artifact directly from Xtend (Verdict Inspector + VASE).

    Called exclusively by the Xtend layer after Balmathic κ promotion decision.
    Skips WARF arbitration — scoring already happened upstream. Deposits the
    winning artifact directly into the reason:// registry.
    """
    _validate_uri(req.address)

    uri_match = REASON_URI_PATTERN.match(req.address)
    domain = uri_match.group(1)
    category = uri_match.group(2)
    task = uri_match.group(3)

    artifact_id = uuid.uuid4().hex
    deposited_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Re-derive audit hash chaining Xtend's hash into this deposit record
    audit_payload = f"{artifact_id}|{req.address}|{req.pcf_score:.6f}|{req.agent_id}|{deposited_at}|{req.audit_hash}"
    audit_hash = hashlib.sha256(audit_payload.encode()).hexdigest()

    metadata = {
        **req.metadata,
        "flow_type": req.flow_type,
        "balmathic_kappa": req.balmathic_kappa,
        "xtend_audit_hash": req.audit_hash,
    }

    db = get_db()
    _exec(
        db,
        _upsert_artifact_sql(),
        (
            artifact_id,
            req.address,
            domain,
            category,
            task,
            json.dumps(req.payload.get("pattern", [])),
            json.dumps(req.payload.get("thresholds", {})),
            req.pcf_score,
            req.payload.get("n_examples", 0),
            req.agent_id,
            deposited_at,
            audit_hash,
            json.dumps(metadata),
        ),
    )
    db.commit()
    db.close()

    return {
        "status": "promoted",
        "artifact_id": artifact_id,
        "address": req.address,
        "reason_dot_uri": req.address,
        "pcf_score": req.pcf_score,
        "balmathic_kappa": req.balmathic_kappa,
        "flow_type": req.flow_type,
        "deposited_at": deposited_at,
        "audit_hash": audit_hash,
    }
