"""
ReasonClient — Python client for the reason:// protocol.

Provides resolve() and register() as the primary interface for
interacting with the reason:// namespace registry via an Xport node.

Usage:
    from reason_py import ReasonClient

    client = ReasonClient(endpoint="https://xport.astrognosy.com")

    # Resolve a named reasoning artifact
    artifact = client.resolve("reason://finance/fraud/anomaly-detection")

    # Use the artifact
    for transaction in my_data:
        similarity = compute_similarity(transaction.features, artifact.pattern)
        if similarity > artifact.thresholds.high_confidence:
            flag(transaction)
"""

import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional

from .models import ReasonArtifact

# Default endpoint — Astrognosy's reference Xport node (Node 0)
DEFAULT_ENDPOINT = "https://xport.astrognosy.com"

# Valid reason:// URI pattern
URI_PATTERN = re.compile(
    r"^reason://([a-z][a-z0-9-]{1,62})/([a-z][a-z0-9-]{1,62})/([a-z][a-z0-9-]{1,62})$"
)


class ReasonURIError(ValueError):
    """Raised when a reason:// URI is malformed."""
    pass


class ReasonResolutionError(Exception):
    """Raised when resolution fails (URI not found, node error, etc)."""
    pass


class ReasonRegistrationError(Exception):
    """Raised when artifact registration fails."""
    pass


class ReasonClient:
    """
    Client for the reason:// reasoning namespace protocol.

    Connects to an Xport node to resolve named reasoning artifacts
    and register new artifacts (via arbitration).

    Args:
        endpoint: Base URL of the Xport node to connect to.
                  Defaults to Astrognosy's reference node (Node 0).
        timeout:  Request timeout in seconds. Default: 30.
        api_key:  Optional API key for authenticated endpoints.
    """

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        timeout: int = 30,
        api_key: Optional[str] = None,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve(self, uri: str, bypass_cache: bool = False) -> ReasonArtifact:
        """
        Resolve a reason:// URI to the best-supported reasoning artifact.

        Connects to the configured Xport node and retrieves the artifact
        with the highest convergence score currently registered under the
        given URI. If the node has a cached result (RDN hit), it is
        returned immediately without a store lookup.

        Resolution does not trigger new arbitration. Scores are immutable
        from deposit time. This is a lookup operation, not a scoring
        operation.

        Args:
            uri:          A valid reason:// URI.
                          Format: reason://<domain>/<category>/<task>
            bypass_cache: If True, skip the RDN cache and perform a
                          fresh store lookup. Use only when freshness is
                          operationally required — adds latency.

        Returns:
            ReasonArtifact: The best-supported artifact for this URI.

        Raises:
            ReasonURIError:        URI is malformed.
            ReasonResolutionError: URI not found, no admitted artifacts,
                                   or node error.

        Example:
            artifact = client.resolve("reason://medicine/records/longitudinal-maintenance-prediction")
            print(f"Score: {artifact.score}")
            print(f"Deposited by: {artifact.provenance.agent_id}")
            print(f"Evidence count: {artifact.metadata.evidence_count}")
        """
        self._validate_uri(uri)

        encoded_uri = urllib.parse.quote(uri, safe="")
        url = f"{self.endpoint}/resolve?address={encoded_uri}"
        if bypass_cache:
            url += "&bypass_cache=true"

        response = self._get(url)
        return ReasonArtifact.from_dict(response)

    def register(self, uri: str, artifact: ReasonArtifact) -> bool:
        """
        Register a reasoning artifact under a reason:// URI.

        An artifact may only be registered if it has won a live
        arbitration round. The arbitration event ID and audit hash
        in the artifact's provenance are verified by the Xport node
        before registration is accepted.

        There is no direct deposit path. Submitting an artifact that
        has not won arbitration will return False.

        Args:
            uri:      The reason:// URI to register under.
            artifact: The ReasonArtifact to register. Must include
                      valid provenance with an arbitration_event_id
                      and audit_hash.

        Returns:
            True if registration succeeded; False otherwise.

        Raises:
            ReasonURIError:            URI is malformed.
            ReasonRegistrationError:   Node rejected the registration
                                       (arbitration not verified, etc).

        Example:
            # After winning an arbitration round on an Xport node:
            success = client.register(
                "reason://manufacturing/bearing/fault-signature",
                my_artifact
            )
        """
        self._validate_uri(uri)

        url = f"{self.endpoint}/register"
        payload = {
            "address": uri,
            "pattern": artifact.pattern,
            "thresholds": {
                "high_confidence": artifact.thresholds.high_confidence,
                "moderate_confidence": artifact.thresholds.moderate_confidence,
                "minimum_signal": artifact.thresholds.minimum_signal,
            },
            "n_examples": artifact.metadata.evidence_count,
            "agent_id": artifact.provenance.agent_id,
            "task_description": (
                f"{artifact.metadata.domain}/{artifact.metadata.category}"
                f"/{artifact.metadata.task}"
            ),
            "metadata": {
                "evidence_count": artifact.metadata.evidence_count,
                "domain": artifact.metadata.domain,
                "category": artifact.metadata.category,
                "task": artifact.metadata.task,
                "version": artifact.metadata.version,
            },
        }

        try:
            response = self._post(url, payload)
            return response.get("status") == "deposited"
        except ReasonRegistrationError:
            raise
        except Exception as exc:
            raise ReasonRegistrationError(
                f"Registration failed for {uri}: {exc}"
            ) from exc

    def get_audit_record(self, arbitration_event_id: str) -> str:
        """
        Retrieve the raw audit record for an arbitration event.

        The returned string can be SHA-256 hashed and compared
        against the audit_hash in an artifact's provenance to
        independently verify the artifact's score.

        Args:
            arbitration_event_id: The event ID from an artifact's provenance.

        Returns:
            Raw audit record string.

        Example:
            record = client.get_audit_record(artifact.provenance.arbitration_event_id)
            computed = "sha256:" + hashlib.sha256(record.encode()).hexdigest()
            assert computed == artifact.provenance.audit_hash
        """
        encoded_id = urllib.parse.quote(arbitration_event_id, safe="")
        url = f"{self.endpoint}/audit/{encoded_id}"
        response = self._get(url)
        return response.get("record", "")

    def list_artifacts(self, uri: str) -> list:
        """
        List all artifacts registered under a reason:// URI.

        Returns all admitted artifacts (not just the current leader),
        ordered by score descending.

        Args:
            uri: A valid reason:// URI.

        Returns:
            List of ReasonArtifact objects, ordered by score descending.
        """
        self._validate_uri(uri)

        encoded_uri = urllib.parse.quote(uri, safe="")
        url = f"{self.endpoint}/artifacts?address={encoded_uri}"
        response = self._get(url)
        artifacts_data = response if isinstance(response, list) else response.get("artifacts", [])
        return [ReasonArtifact.from_dict(a) for a in artifacts_data]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_uri(uri: str) -> None:
        """Validate that a string is a well-formed reason:// URI."""
        if not URI_PATTERN.match(uri):
            raise ReasonURIError(
                f"Invalid reason:// URI: {uri!r}\n"
                f"Expected format: reason://<domain>/<category>/<task>\n"
                f"All segments must be lowercase with hyphens only."
            )

    def _get(self, url: str) -> dict:
        """Perform a GET request and return parsed JSON."""
        req = urllib.request.Request(url, method="GET")
        self._add_headers(req)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                err = json.loads(body)
                code = err.get("error", "unknown_error")
            except Exception:
                code = "unknown_error"
            if exc.code == 404:
                raise ReasonResolutionError(
                    f"Not found ({code}): {url}"
                ) from exc
            raise ReasonResolutionError(
                f"HTTP {exc.code} from node: {code}"
            ) from exc
        except urllib.error.URLError as exc:
            raise ReasonResolutionError(
                f"Node unreachable at {self.endpoint}: {exc.reason}"
            ) from exc

    def _post(self, url: str, payload: dict) -> dict:
        """Perform a POST request with JSON body and return parsed JSON."""
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        self._add_headers(req)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                err = json.loads(body)
                detail = err.get("detail", err.get("error", "unknown_error"))
            except Exception:
                detail = "unknown_error"
            raise ReasonRegistrationError(
                f"HTTP {exc.code} from node: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise ReasonRegistrationError(
                f"Node unreachable at {self.endpoint}: {exc.reason}"
            ) from exc

    def _add_headers(self, req: urllib.request.Request) -> None:
        """Add authentication headers to a request if api_key is set."""
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")

    def compare(self, features: List[float], artifact: ReasonArtifact) -> float:
        """
        Compute cosine similarity between a feature vector and an artifact's pattern.

        Local operation — no network I/O. Use to measure how closely a local
        observation matches the reasoning pattern in a resolved artifact.

        Args:
            features: Feature vector from a local observation.
            artifact: A ReasonArtifact returned by resolve().

        Returns:
            Cosine similarity in [0.0, 1.0]. Returns 0.0 for zero-norm vectors.
        """
        pattern = artifact.pattern
        dot = sum(a * b for a, b in zip(features, pattern))
        norm_f = sum(a * a for a in features) ** 0.5
        norm_p = sum(b * b for b in pattern) ** 0.5
        if norm_f == 0.0 or norm_p == 0.0:
            return 0.0
        return dot / (norm_f * norm_p)
