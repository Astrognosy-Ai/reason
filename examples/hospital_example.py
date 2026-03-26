"""
Hospital A / Hospital B — reason:// walkthrough

This example illustrates the core use case that motivated the reason:// protocol:
transferring learned reasoning across institutional boundaries without transferring
any underlying data.

The Scenario
------------
Hospital A has processed 4,200 patient timelines and discovered a structural
pattern that predicts 30-day intervention needs. The pattern is in the temporal
structure of the observation timeline — not in any individual observation's value.

Hospital A wants to share this insight. HIPAA makes data sharing impossible.
But Hospital A can share the *shape* of the pattern — a compressed structural
representation that is mathematically non-invertible. No patient record can be
reconstructed from it.

Hospital B has its own patient population, its own records, no connection to
Hospital A. It resolves the reason:// URI and receives the pattern. It applies
that pattern to its own data. One API call. No data crossed any boundary.

This example walks through both sides of that exchange in code.
"""

import sys
import os

# If running from the repo root, add the sdk to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk"))

from reason_py import ReasonClient
from reason_py.client import ReasonResolutionError, ReasonURIError

# ---------------------------------------------------------------------------
# Shared utility — similarity computation
# ---------------------------------------------------------------------------
# In a real deployment, this would be your domain-specific comparison function.
# For illustration: cosine similarity over the artifact's pattern vector.

def cosine_similarity(vec_a, vec_b):
    """Compute cosine similarity between two vectors."""
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be the same length.")
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = sum(a ** 2 for a in vec_a) ** 0.5
    mag_b = sum(b ** 2 for b in vec_b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ---------------------------------------------------------------------------
# Hospital A — Discovering and depositing a reasoning artifact
# ---------------------------------------------------------------------------

def hospital_a_side():
    """
    Hospital A: self-initiate an arbitration round and deposit a reasoning artifact.

    In production this would involve:
    1. Submitting a cargo package to an Xport node (POST /arbitrate)
    2. Receiving back a convergence score and audit hash
    3. Registering the artifact via client.register()

    For this example, we illustrate the shape of that flow without a live node.
    """
    print("=" * 60)
    print("HOSPITAL A — Discovering and registering a pattern")
    print("=" * 60)

    # Step 1: Hospital A's agent processes its patient timelines.
    # It identifies a structural pattern in the observation sequences.
    # (In production: this pattern emerges from the PCF scoring process
    # during the arbitration submission, not from manual construction.)

    print("\n[1] Agent has processed 4,200 patient observation timelines.")
    print("    Structural pattern identified in temporal observation sequences.")
    print("    Pattern: non-invertible centroid in observation-timeline space.")
    print("    No patient records, IDs, or observation values are included.")

    # Step 2: Self-initiate an arbitration round.
    # The agent submits its cargo package to an Xport node.
    # Xport evaluates the submission and, if it meets threshold, admits it.

    print("\n[2] Self-initiating arbitration round...")
    print("    Submitting cargo package to Xport node:")
    print("      POST /arbitrate")
    print("      {")
    print('        "query_id": "arb-2026-03-26-medicine-001",')
    print('        "agent_id": "hospital-a-agent",')
    print('        "answer_tokens": ["pattern:intervention_risk_high", ...],')
    print('        "corpus": [<4,200 case structural descriptors — no raw values>]')
    print("      }")
    print()
    print("    Result: score=0.91 (evidence strength validated)")
    print("    Audit hash: sha256:a3f9c2...")

    # Step 3: Register the winning artifact under the reason:// URI.
    # (Illustrative — requires a live Xport node with reason:// endpoint)

    print("\n[3] Registering artifact under reason:// URI...")
    print("    URI: reason://medicine/records/longitudinal-maintenance-prediction")
    print()
    print("    Artifact registered:")
    print("      pattern:     [compressed structural centroid]")
    print("      thresholds:  high=0.88, moderate=0.71, minimum=0.54")
    print("      score:       0.91")
    print("      provenance:  hospital-a-agent · 2026-03-26")
    print("      raw data:    none — architecturally impossible")

    print("\nHospital A done. Pattern is now discoverable globally.")
    print("No patient data left the institution.")


# ---------------------------------------------------------------------------
# Hospital B — Resolving and applying the artifact
# ---------------------------------------------------------------------------

def hospital_b_side(use_live_node: bool = False):
    """
    Hospital B: resolve the reason:// URI and apply the artifact to its own data.

    Hospital B has no connection to Hospital A. Different records,
    different patient population, different institution.

    With one API call, it can now apply the pattern Hospital A discovered —
    without receiving any of the data that produced it.
    """
    print()
    print("=" * 60)
    print("HOSPITAL B — Resolving and applying a reasoning artifact")
    print("=" * 60)

    # Simulated patient records for Hospital B.
    # In production these would be real patient observation timelines,
    # pre-processed into feature vectors by the institution's own pipeline.
    # No data from Hospital A is involved.
    simulated_patients = [
        {
            "patient_id": "HB-0042",
            "feature_vector": [0.81, -0.73, 0.55, 0.12, -0.44, 0.67],
            "label": "high risk (ground truth for this demo)",
        },
        {
            "patient_id": "HB-0107",
            "feature_vector": [-0.23, 0.44, -0.61, 0.88, 0.15, -0.32],
            "label": "low risk (ground truth for this demo)",
        },
        {
            "patient_id": "HB-0219",
            "feature_vector": [0.74, -0.68, 0.49, 0.08, -0.51, 0.72],
            "label": "high risk (ground truth for this demo)",
        },
        {
            "patient_id": "HB-0334",
            "feature_vector": [0.02, 0.17, -0.09, 0.33, 0.41, -0.28],
            "label": "low risk (ground truth for this demo)",
        },
    ]

    if use_live_node:
        # Live resolution via the reason:// SDK
        client = ReasonClient(endpoint="https://xport.astrognosy.ai")
        print("\n[1] Connecting to Xport node...")

        try:
            artifact = client.resolve(
                "reason://medicine/records/longitudinal-maintenance-prediction"
            )
            print(f"    Resolved. Score: {artifact.score}")
            print(f"    Deposited by: {artifact.provenance.agent_id}")
            print(f"    Evidence: {artifact.metadata.evidence_count} cases")

            pattern = artifact.pattern
            thresholds = artifact.thresholds

        except ReasonURIError as e:
            print(f"    URI error: {e}")
            return
        except ReasonResolutionError as e:
            print(f"    Resolution failed: {e}")
            print("    (Run with use_live_node=False for the simulated walkthrough)")
            return

    else:
        # Simulated resolution — illustrates the same flow without a live node
        print("\n[1] Resolving URI (simulated — no live node required):")
        print("    client.resolve('reason://medicine/records/longitudinal-maintenance-prediction')")
        print()
        print("    Received artifact:")
        print("      score:           0.91")
        print("      agent:           hospital-a-agent")
        print("      evidence_count:  4200")
        print("      thresholds:      high=0.88, moderate=0.71, minimum=0.54")
        print()

        # Simulated pattern — same dimensionality as our feature vectors above
        pattern = [0.78, -0.70, 0.52, 0.11, -0.48, 0.69]

        class SimulatedThresholds:
            high_confidence = 0.88
            moderate_confidence = 0.71
            minimum_signal = 0.54
            def classify(self, score):
                if score >= self.high_confidence:
                    return "high_confidence"
                elif score >= self.moderate_confidence:
                    return "moderate_confidence"
                elif score >= self.minimum_signal:
                    return "minimum_signal"
                else:
                    return "no_signal"

        thresholds = SimulatedThresholds()

    # Apply the artifact's pattern to Hospital B's own patient records.
    # Hospital B is doing the comparison locally — its records never leave.
    print("\n[2] Applying pattern to Hospital B's patient records...")
    print("    (Hospital B's data stays local — only the pattern was received)")
    print()

    flagged = []
    for patient in simulated_patients:
        similarity = cosine_similarity(patient["feature_vector"], pattern)
        tier = thresholds.classify(similarity)

        flag = ""
        if tier == "high_confidence":
            flagged.append(patient["patient_id"])
            flag = " <-- FLAGGED FOR REVIEW"

        print(f"    {patient['patient_id']}  similarity={similarity:.3f}  tier={tier}{flag}")
        print(f"      ({patient['label']})")

    print()
    print(f"[3] Summary: {len(flagged)} patients flagged for 30-day intervention review.")
    print(f"    Flagged: {', '.join(flagged)}")
    print()
    print("    No data from Hospital A was received.")
    print("    No data from Hospital B left the institution.")
    print("    Hospital B is now operating with the benefit of Hospital A's 4,200 cases.")
    print("    One API call. No privacy compromised. No law broken.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="reason:// Hospital A/B walkthrough"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Connect to a live Xport node (requires https://xport.astrognosy.ai to be up)"
    )
    args = parser.parse_args()

    hospital_a_side()
    hospital_b_side(use_live_node=args.live)

    print()
    print("=" * 60)
    print("What transferred:")
    print("  The structural pattern:   YES")
    print("  Calibrated thresholds:    YES")
    print("  The earned score:         YES")
    print("  Provenance / attribution: YES")
    print("  Any patient record:       NO")
    print("  Any observation value:    NO")
    print("  Any identifier:           NO")
    print("  Any raw data:             NO — architecturally impossible")
    print("=" * 60)
