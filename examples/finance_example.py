"""
Finance — Fraud anomaly detection via reason://

This example demonstrates how a financial institution can resolve a
fraud detection reasoning artifact from the reason:// registry and
apply it to its own transaction data — without receiving any
transaction records from the institutions that produced the artifact.

The Use Case
------------
A mid-size regional bank wants to improve its fraud detection. Training
its own anomaly detection model from scratch would require years of
labeled fraud cases that it may not have in sufficient volume.

The reason:// registry contains an artifact under:
  reason://finance/fraud/anomaly-detection

This artifact was produced by an agent that processed 92,000 transaction
cases (labeled fraud/not-fraud) and won a competitive arbitration round
on the strength of that evidence. Its score: 0.89.

The bank's agent resolves the URI, receives the structural pattern,
applies it to its own transaction stream, and flags anomalies for review.

No transaction records from the depositing institution were received.
No transaction records from the bank leave the bank.
"""

import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk"))

from reason_py import ReasonClient
from reason_py.client import ReasonResolutionError, ReasonURIError


# ---------------------------------------------------------------------------
# Simulated transaction feature extraction
# ---------------------------------------------------------------------------
# In production, your institution's pipeline converts raw transactions into
# feature vectors using your own internal logic. The artifact's pattern
# operates in this feature space.

def extract_features(transaction: dict) -> list:
    """
    Extract a normalized feature vector from a transaction record.

    Features here are illustrative — a real implementation would use
    domain-specific signals: amount, velocity, merchant category, etc.
    """
    return [
        transaction.get("amount_normalized", 0.0),
        transaction.get("velocity_score", 0.0),
        transaction.get("geo_deviation", 0.0),
        transaction.get("time_of_day_score", 0.0),
        transaction.get("merchant_risk_score", 0.0),
        transaction.get("device_fingerprint_score", 0.0),
    ]


def cosine_similarity(vec_a, vec_b):
    """Cosine similarity between two feature vectors."""
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be same length.")
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = sum(a ** 2 for a in vec_a) ** 0.5
    mag_b = sum(b ** 2 for b in vec_b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ---------------------------------------------------------------------------
# Simulated transaction stream
# ---------------------------------------------------------------------------

# Simulated transactions for the regional bank.
# These stay local — they are never sent anywhere.
SIMULATED_TRANSACTIONS = [
    {
        "txn_id": "TXN-8821",
        "amount_normalized": 0.92,
        "velocity_score": 0.88,
        "geo_deviation": 0.79,
        "time_of_day_score": 0.84,
        "merchant_risk_score": 0.91,
        "device_fingerprint_score": 0.77,
        "ground_truth": "fraud",
    },
    {
        "txn_id": "TXN-4412",
        "amount_normalized": 0.12,
        "velocity_score": 0.08,
        "geo_deviation": 0.03,
        "time_of_day_score": 0.45,
        "merchant_risk_score": 0.11,
        "device_fingerprint_score": 0.19,
        "ground_truth": "legitimate",
    },
    {
        "txn_id": "TXN-9034",
        "amount_normalized": 0.85,
        "velocity_score": 0.79,
        "geo_deviation": 0.88,
        "time_of_day_score": 0.91,
        "merchant_risk_score": 0.83,
        "device_fingerprint_score": 0.86,
        "ground_truth": "fraud",
    },
    {
        "txn_id": "TXN-2201",
        "amount_normalized": 0.31,
        "velocity_score": 0.22,
        "geo_deviation": 0.17,
        "time_of_day_score": 0.58,
        "merchant_risk_score": 0.28,
        "device_fingerprint_score": 0.35,
        "ground_truth": "legitimate",
    },
    {
        "txn_id": "TXN-5577",
        "amount_normalized": 0.76,
        "velocity_score": 0.81,
        "geo_deviation": 0.71,
        "time_of_day_score": 0.88,
        "merchant_risk_score": 0.74,
        "device_fingerprint_score": 0.69,
        "ground_truth": "fraud",
    },
    {
        "txn_id": "TXN-3309",
        "amount_normalized": 0.05,
        "velocity_score": 0.14,
        "geo_deviation": 0.08,
        "time_of_day_score": 0.61,
        "merchant_risk_score": 0.09,
        "device_fingerprint_score": 0.22,
        "ground_truth": "legitimate",
    },
]


# ---------------------------------------------------------------------------
# Main example
# ---------------------------------------------------------------------------

def run_finance_example(use_live_node: bool = False):
    """
    Resolve the fraud anomaly detection artifact and apply it to transactions.
    """
    print("=" * 60)
    print("FRAUD DETECTION — reason:// walkthrough")
    print("=" * 60)
    print()
    print("Institution: Regional Bank (no existing fraud model)")
    print("URI:         reason://finance/fraud/anomaly-detection")
    print()

    if use_live_node:
        client = ReasonClient(endpoint="https://reason.astrognosy.com")
        print("[1] Resolving artifact from live node...")

        try:
            artifact = client.resolve("reason://finance/fraud/anomaly-detection")
            pattern = artifact.pattern
            thresholds = artifact.thresholds
            print(f"    Score:          {artifact.score}")
            print(f"    Agent:          {artifact.provenance.agent_id}")
            print(f"    Evidence cases: {artifact.metadata.evidence_count:,}")
            print(f"    Thresholds:     high={thresholds.high_confidence}, "
                  f"moderate={thresholds.moderate_confidence}, "
                  f"minimum={thresholds.minimum_signal}")

        except ReasonURIError as e:
            print(f"    URI error: {e}")
            return
        except ReasonResolutionError as e:
            print(f"    Resolution failed: {e}")
            print("    Run with use_live_node=False for the simulated walkthrough.")
            return

    else:
        # Simulated resolution
        print("[1] Resolving artifact (simulated):")
        print("    client.resolve('reason://finance/fraud/anomaly-detection')")
        print()
        print("    Received:")
        print("      score:           0.89")
        print("      agent:           fincorp-fraud-agent-v2")
        print("      evidence_count:  92,000 transactions")
        print("      thresholds:      high=0.84, moderate=0.67, minimum=0.51")
        print()

        # Simulated pattern — matches our 6-feature vector space
        pattern = [0.88, 0.82, 0.83, 0.89, 0.85, 0.80]

        class SimulatedThresholds:
            high_confidence = 0.84
            moderate_confidence = 0.67
            minimum_signal = 0.51
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

    # Apply the artifact to the bank's own transaction stream
    print("[2] Applying artifact to transaction stream...")
    print("    (All transactions stay local — only the pattern was received)")
    print()

    results = []
    for txn in SIMULATED_TRANSACTIONS:
        features = extract_features(txn)
        similarity = cosine_similarity(features, pattern)
        tier = thresholds.classify(similarity)

        results.append({
            "txn_id": txn["txn_id"],
            "similarity": similarity,
            "tier": tier,
            "ground_truth": txn["ground_truth"],
        })

    # Display results
    print(f"    {'TXN ID':<12}  {'SIMILARITY':>10}  {'TIER':<20}  {'GROUND TRUTH':<12}")
    print(f"    {'-'*12}  {'-'*10}  {'-'*20}  {'-'*12}")
    for r in results:
        flag = " <-- FLAGGED" if r["tier"] in ("high_confidence", "moderate_confidence") else ""
        print(
            f"    {r['txn_id']:<12}  {r['similarity']:>10.3f}  {r['tier']:<20}  "
            f"{r['ground_truth']:<12}{flag}"
        )

    # Summary
    flagged = [r for r in results if r["tier"] in ("high_confidence", "moderate_confidence")]
    correctly_flagged = [r for r in flagged if r["ground_truth"] == "fraud"]
    true_frauds = [r for r in results if r["ground_truth"] == "fraud"]

    print()
    print(f"[3] Summary:")
    print(f"    Transactions evaluated: {len(results)}")
    print(f"    Flagged for review:     {len(flagged)}")
    print(f"    Correctly flagged:      {len(correctly_flagged)} of {len(true_frauds)} frauds")
    print()
    print("    The bank now has fraud detection capability backed by 92,000 labeled")
    print("    cases from an institution it has never interacted with.")
    print()
    print("    No transaction records were received from the depositing institution.")
    print("    No transaction records left the bank.")
    print("    One API call. No data crossed any boundary.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="reason:// fraud detection example"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Connect to a live reason:// registry node (requires https://reason.astrognosy.com)"
    )
    args = parser.parse_args()

    run_finance_example(use_live_node=args.live)
