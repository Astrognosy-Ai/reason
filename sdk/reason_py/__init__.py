from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import requests
import hashlib
from datetime import datetime
import warnings

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

@dataclass
class ReasonArtifact:
    """A validated reasoning artifact from the reason:// registry.
    Contains ONLY the non-invertible structural pattern — never raw data."""
    address: str
    pattern: List[float]                    # compressed structural centroid
    thresholds: Dict[str, float]            # e.g. {"high_confidence": 0.85, ...}
    score: float                            # PCF arbitration score 0-1
    confidence: float                       # calibrated from n examples
    provenance: Dict[str, str]              # who deposited it, when
    metadata: Dict[str, Any]                # public, non-sensitive only

    @classmethod
    def from_json(cls, data: Dict) -> "ReasonArtifact":
        return cls(**data)

class ReasonClient:
    """Official reference client for reason:// (CC BY 4.0)"""

    def __init__(self, registry_url: str = "https://registry.reason.pub/v1"):
        self.registry_url = registry_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "reason-py/0.1.0"})

    def resolve(self, address: str) -> ReasonArtifact:
        """One-line fetch of a validated structural reasoning artifact.
        Example: reason://medicine/records/longitudinal-maintenance-prediction"""
        if not address.startswith("reason://"):
            raise ValueError("Address must start with 'reason://'")

        resp = self.session.get(f"{self.registry_url}/resolve", params={"address": address})
        resp.raise_for_status()
        return ReasonArtifact.from_json(resp.json())

    def build_tokenized_corpus(self, structural_descriptions: List[str]) -> Dict:
        """Local-only tokenization. Never sends raw data — only structural tokens."""
        tokens = []
        for desc in structural_descriptions:
            # Replace this hash with your real PCF structural encoder in production
            token = hashlib.sha256(desc.encode("utf-8")).hexdigest()[:32]
            tokens.append(token)
        return {"tokens": tokens, "n_structural": len(tokens)}

    def submit_self_initiated(self, address: str, structural_corpus: List[str],
                              n_examples: int, task_description: str) -> Dict:
        """Self-initiated arbitration round — exactly as described in the explainer."""
        tokens = self.build_tokenized_corpus(structural_corpus)
        payload = {
            "address": address,
            "tokens": tokens["tokens"],
            "n_examples": n_examples,
            "task_description": task_description,
            "timestamp": datetime.utcnow().isoformat()
        }
        resp = self.session.post(f"{self.registry_url}/arbitrate/self", json=payload)
        resp.raise_for_status()
        result = resp.json()
        if result.get("status") == "won":
            print(f"Artifact deposited: {address} (score: {result.get('score')})")
        return result

    def compare(self, local_embedding: List[float], artifact: ReasonArtifact) -> float:
        """Local comparison of your embedding against the structural centroid.
        Uses cosine similarity (swap for your exact PCF compare function)."""
        if not NUMPY_AVAILABLE:
            warnings.warn("numpy not installed — falling back to pure Python (slower)")
            dot = sum(a * b for a, b in zip(local_embedding, artifact.pattern))
            norm_a = (sum(x*x for x in local_embedding)) ** 0.5
            norm_b = (sum(x*x for x in artifact.pattern)) ** 0.5
            return dot / (norm_a * norm_b + 1e-8) if norm_a and norm_b else 0.0

        a = np.array(local_embedding)
        b = np.array(artifact.pattern)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

# Quick example that mirrors the live reason:// demo tab
if __name__ == "__main__":
    client = ReasonClient()
    artifact = client.resolve("reason://medicine/records/longitudinal-maintenance-prediction")
    print(f"Loaded artifact from {artifact.provenance['agent']} — score {artifact.score}")

    # Your local data only
    for patient in my_patient_timelines:          # <- your own data
        score = client.compare(patient.embedding, artifact)
        if score > artifact.thresholds.get("high_confidence", 0.85):
            flag_for_review(patient)
