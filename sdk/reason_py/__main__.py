"""
reason_py -- CLI entry point.

Usage:
    python -m reason_py
    reason-py
"""

from reason_py import __version__


LOGO = r"""

                                                                                    d8    d8
                                                                                  ,8P'  ,8P'
                                                                                 d8"   d8"
8b,dPPYba,   ,adPPYba,  ,adPPYYba,  ,adPPYba,   ,adPPYba,   8b,dPPYba,   888       ,8P'  ,8P'
88P'   "Y8  a8P_____88  ""     `Y8  I8[    ""  a8"     "8a  88P'   `"8a  888      d8"   d8"
88          8PP"""""""  ,adPPPPP88   `"Y8ba,   8b       d8  88       88         ,8P'  ,8P'
88          "8b,   ,aa  88,    ,88  aa    ]8I  "8a,   ,a8"  88       88  888   d8"   d8"
88           `"Ybbd8"'  `"8bbdP"Y8  `"YbbdP"'   `"YbbdP"'   88       88  888  8P'   8P'

"""

HELP = """
{logo}
  reason_py {version} -- Python client for the reason:// protocol
  https://reason.astrognosy.com


INSTALL
-------
  $ pip install reason-py


QUICK START
-----------
  $ python

  >>> from reason_py import ReasonClient
  >>> client = ReasonClient()
  >>> artifact = client.resolve("reason://finance/fraud/anomaly-detection")
  >>> features = [0.12, 0.95, 0.03, 0.41, 0.78, 0.56]   # your feature vector
  >>> similarity = client.compare(features, artifact)
  >>> similarity > artifact.thresholds.high_confidence    # True = flag it
  True


METHODS
-------
  client.resolve(uri: str) -> ReasonArtifact
      Fetch the best admitted artifact for a reason:// URI.

  client.compare(features: list, artifact: ReasonArtifact) -> float
      Cosine similarity between your feature vector and the artifact pattern.
      Returns float in [0.0, 1.0].  Local -- no network I/O.

  client.list_artifacts(uri: str) -> list
      All admitted artifacts under a URI, ordered by score descending.

  client.register(uri: str, artifact: ReasonArtifact) -> bool
      Register an artifact after winning WARF arbitration.

  client.get_audit_record(event_id: str) -> str
      Fetch the raw audit record for hash verification.


ARTIFACT FIELDS
---------------
  artifact.uri                              reason:// address
  artifact.pattern                          structural centroid (list of floats)
  artifact.score                            PCF convergence score [0.0, 1.0]
  artifact.thresholds.high_confidence       similarity threshold -- flag
  artifact.thresholds.moderate_confidence   similarity threshold -- review
  artifact.thresholds.minimum_signal        similarity threshold -- detect
  artifact.provenance.agent_id              depositing agent
  artifact.provenance.audit_hash            sha256:... verifiable hash
  artifact.metadata.evidence_count          training examples used
  artifact.metadata.version                 artifact version at this URI


LIVE URIS
---------
  reason://finance/fraud/anomaly-detection
  reason://cybersecurity/network/port-scan-classification
  reason://medicine/records/longitudinal-maintenance-prediction

  Live node: https://xport.astrognosy.com


LINKS
-----
  Docs:   https://reason.astrognosy.com
  GitHub: https://github.com/Astrognosy-Ai/reason
  PyPI:   https://pypi.org/project/reason-py/
  IETF:   draft-westerbeck-reason-protocol
"""


def main():
    print(HELP.format(logo=LOGO, version=__version__))


if __name__ == "__main__":
    main()
