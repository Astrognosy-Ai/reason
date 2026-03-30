"""
reason_py — CLI entry point.

Usage:
    python -m reason_py
    reason-py
"""

from reason_py import __version__


HELP = f"""
reason_py {__version__} — Python client for the reason:// protocol
https://reason.astrognosy.com

QUICK START
-----------
  from reason_py import ReasonClient

  client = ReasonClient()
  artifact = client.resolve("reason://finance/fraud/anomaly-detection")
  similarity = client.compare(my_features, artifact)

LIVE NODE
---------
  https://xport.astrognosy.com
  (Astrognosy AI — Node 0, reference implementation)

METHODS
-------
  client.resolve(uri)
      Fetch the best artifact for a reason:// URI.
      Returns: ReasonArtifact

  client.compare(features, artifact)
      Cosine similarity between a feature vector and an artifact pattern.
      Local — no network I/O.
      Returns: float in [0.0, 1.0]

  client.list_artifacts(uri)
      All admitted artifacts under a URI, ordered by score descending.
      Returns: list[ReasonArtifact]

  client.register(uri, artifact)
      Register an artifact after winning WARF arbitration.
      Returns: bool

  client.get_audit_record(event_id)
      Fetch the raw audit record for hash verification.
      Returns: str

ARTIFACT FIELDS
---------------
  artifact.uri                              reason:// address
  artifact.pattern                          structural centroid (list of floats)
  artifact.score                            PCF convergence score [0, 1]
  artifact.thresholds.high_confidence       similarity threshold — flag
  artifact.thresholds.moderate_confidence   similarity threshold — review
  artifact.thresholds.minimum_signal        similarity threshold — detect
  artifact.provenance.agent_id              depositing agent
  artifact.provenance.audit_hash            sha256:... verifiable hash
  artifact.metadata.evidence_count          training examples used
  artifact.metadata.version                 artifact version at this URI

LIVE URIS (resolvable now)
--------------------------
  reason://finance/fraud/anomaly-detection
  reason://cybersecurity/network/port-scan-classification
  reason://medicine/records/longitudinal-maintenance-prediction

LINKS
-----
  Docs:   https://reason.astrognosy.com
  GitHub: https://github.com/Astrognosy-Ai/reason
  PyPI:   https://pypi.org/project/reason-py/
  IETF:   draft-westerbeck-reason-protocol
"""


def main():
    print(HELP)


if __name__ == "__main__":
    main()
