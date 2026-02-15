"""
Evaluation Test Script

Runs the prescription pipeline on sample data and produces a summary table
with metrics for parsing quality, grounding coverage, and system evaluation.

Usage:
    python tests/test_evaluation.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.evaluation import compute_parsing_f1, compute_grounding_coverage
from modules.confidence_scorer import compute_confidence


# ==============================
# Sample Ground Truth Data
# ==============================

SAMPLE_PRESCRIPTIONS = [
    {
        "name": "Sample 1 — Oncology",
        "parsed": {
            "patient_info": {"name": "Dalia Kundu", "age": 64, "sex": "F"},
            "diagnosis": "MBC",
            "medications": [
                {"name": "Denosumab", "dose": "120 mg", "frequency": "Monthly"},
                {"name": "Letrozole", "dose": "2.5 mg", "frequency": "Daily"},
            ],
            "follow_up": ["Review after 3 months"]
        },
        "ground_truth": {
            "patient_info": {"name": "Dalia Kundu", "age": 64, "sex": "F"},
            "diagnosis": "Metastatic Breast Cancer",
            "medications": [
                {"name": "Denosumab (Xgeva)", "dose": "120 mg", "frequency": "Once monthly"},
                {"name": "Letrozole", "dose": "2.5 mg", "frequency": "Once daily"},
            ],
            "follow_up": ["Review after 3 months", "Monitor calcium levels"]
        }
    },
    {
        "name": "Sample 2 — Cardiology",
        "parsed": {
            "patient_info": {"name": "Ravi Sharma", "age": 55, "sex": "M"},
            "diagnosis": "HTN",
            "medications": [
                {"name": "Amlodipine", "dose": "5 mg", "frequency": "Once daily"},
                {"name": "Aspirin", "dose": "75 mg", "frequency": "Once daily"},
                {"name": "Atorvastatin", "dose": "20 mg", "frequency": "At night"},
            ],
            "follow_up": ["BP check in 2 weeks"]
        },
        "ground_truth": {
            "patient_info": {"name": "Ravi Sharma", "age": 55, "sex": "M"},
            "diagnosis": "Hypertension with Dyslipidemia",
            "medications": [
                {"name": "Amlodipine", "dose": "5 mg", "frequency": "Once daily"},
                {"name": "Aspirin", "dose": "75 mg", "frequency": "Once daily"},
                {"name": "Atorvastatin", "dose": "20 mg", "frequency": "Once at night"},
            ],
            "follow_up": ["BP check in 2 weeks"]
        }
    },
    {
        "name": "Sample 3 — Diabetes",
        "parsed": {
            "patient_info": {"name": "Meena Joshi", "age": 48, "sex": "F"},
            "diagnosis": "DM Type 2",
            "medications": [
                {"name": "Metformin", "dose": "500 mg", "frequency": "Twice daily"},
                {"name": "Glimepiride", "dose": "1 mg", "frequency": "Before breakfast"},
            ],
            "advice": ["Low sugar diet", "Walk 30 min daily"]
        },
        "ground_truth": {
            "patient_info": {"name": "Meena Joshi", "age": 48, "sex": "F"},
            "diagnosis": "Diabetes Mellitus Type 2",
            "medications": [
                {"name": "Metformin", "dose": "500 mg", "frequency": "Twice daily"},
                {"name": "Glimepiride", "dose": "1 mg", "frequency": "Once before breakfast"},
            ],
            "advice": ["Low sugar diet", "Walk 30 minutes daily"]
        }
    },
]


# ==============================
# Run Evaluation
# ==============================

def run_evaluation():
    print("=" * 70)
    print("  PRESCRIPTION PIPELINE EVALUATION")
    print("=" * 70)

    results = []

    for sample in SAMPLE_PRESCRIPTIONS:
        print(f"\n{'─' * 50}")
        print(f"  {sample['name']}")
        print(f"{'─' * 50}")

        # F1 Score
        f1_result = compute_parsing_f1(sample["parsed"], sample["ground_truth"])
        print(f"  Parsing F1:      {f1_result['f1']:.3f} "
              f"(P={f1_result['precision']:.3f}, R={f1_result['recall']:.3f})")

        # Confidence (makes live API calls)
        try:
            confidence, api_results = compute_confidence(sample["parsed"])
            grounding = compute_grounding_coverage(api_results)

            print(f"  Diagnosis:       {confidence['diagnosis_confidence']} "
                  f"({confidence['diagnosis_reason']})")
            print(f"  Grounding:       {grounding['coverage_percent']}% "
                  f"({grounding['grounded_count']}/{grounding['total_count']})")
            print(f"  Overall:         {confidence['overall_confidence']}")

            results.append({
                "name": sample["name"],
                "f1": f1_result["f1"],
                "precision": f1_result["precision"],
                "recall": f1_result["recall"],
                "diagnosis": confidence["diagnosis_confidence"],
                "grounding": grounding["coverage_percent"],
                "overall": confidence["overall_confidence"]
            })

        except Exception as e:
            print(f"  ⚠ API call failed: {e}")
            results.append({
                "name": sample["name"],
                "f1": f1_result["f1"],
                "precision": f1_result["precision"],
                "recall": f1_result["recall"],
                "diagnosis": "N/A",
                "grounding": "N/A",
                "overall": "N/A"
            })

    # Summary Table
    print(f"\n{'=' * 70}")
    print("  SUMMARY TABLE")
    print(f"{'=' * 70}")
    print(f"  {'Sample':<30} {'F1':>6} {'Diag':>8} {'Ground%':>8} {'Overall':>8}")
    print(f"  {'─' * 62}")

    for r in results:
        g = f"{r['grounding']}%" if isinstance(r['grounding'], (int, float)) else r['grounding']
        print(f"  {r['name']:<30} {r['f1']:>6.3f} {r['diagnosis']:>8} {g:>8} {r['overall']:>8}")

    # Averages
    f1_avg = sum(r["f1"] for r in results) / len(results)
    grounding_vals = [r["grounding"] for r in results if isinstance(r["grounding"], (int, float))]
    grounding_avg = sum(grounding_vals) / len(grounding_vals) if grounding_vals else 0

    print(f"  {'─' * 62}")
    print(f"  {'AVERAGE':<30} {f1_avg:>6.3f} {'':>8} {grounding_avg:>7.1f}% {'':>8}")
    print()


if __name__ == "__main__":
    run_evaluation()
