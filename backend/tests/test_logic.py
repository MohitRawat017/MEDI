"""
Fast pure-logic backend tests.

Runs without API keys, ML models, or a running server, so CI can exercise
the core logic cheaply.

Usage:
    python backend/tests/test_logic.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests

import modules.config as config
from modules.confidence_scorer import compute_grounding_coverage
from modules.evaluation import compute_parsing_f1
from modules.medical_api import (
    fetch_rxnorm_id,
    fetch_dailymed_summary,
    fetch_drug_classes,
    fetch_openfda_interactions,
)

PASS = "PASS"
FAIL = "FAIL"


def test_env_defaults():
    # Import-time defaults must hold when no env vars override them.
    return (
        config.PINECONE_ENV == "us-east-1"
        and config.PINECONE_INDEX_NAME == "medi"
        and config.UPLOAD_DIR == "./uploaded_pdfs"
        and config.ALLOWED_ORIGINS == "*"
    )


def test_grounding_coverage():
    results = [
        {"drug": "A", "rxnorm_id": "x", "dailymed_info": {}},
        {"drug": "B", "rxnorm_id": None, "dailymed_info": None},
    ]
    coverage = compute_grounding_coverage(results)
    return (
        coverage["coverage_percent"] == 50.0
        and coverage["grounded_count"] == 1
        and coverage["total_count"] == 2
        and len(coverage["details"]) == 2
        and compute_grounding_coverage([])["coverage_percent"] == 0.0
    )


def test_parsing_f1():
    ground_truth = {
        "diagnosis": "Hypertension",
        "medications": [{"name": "Aspirin", "dose": "75 mg"}],
    }
    predicted = {
        "diagnosis": "HTN",
        "medications": [{"name": "Aspirin", "dose": "75 mg"}],
    }
    result = compute_parsing_f1(predicted, ground_truth)
    # "aspirin" and "75 mg" match; "htn" vs "hypertension" does not
    return 0.0 < result["f1"] < 1.0 and result["matched"] == 2


class _FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else []

    def json(self):
        return self._payload


def test_api_failure_contract():
    original_get = requests.get
    requests.get = lambda *args, **kwargs: _FakeResponse(payload=[])
    try:
        return (
            fetch_rxnorm_id("X") is None
            and fetch_dailymed_summary("X") is None
            and fetch_drug_classes("X") == []
            and fetch_openfda_interactions("X") == []
        )
    finally:
        requests.get = original_get


def test_api_http_error_contract():
    original_get = requests.get
    requests.get = lambda *args, **kwargs: _FakeResponse(status_code=500)
    try:
        return (
            fetch_rxnorm_id("X") is None
            and fetch_dailymed_summary("X") is None
            and fetch_drug_classes("X") == []
            and fetch_openfda_interactions("X") == []
        )
    finally:
        requests.get = original_get


def main():
    print("=" * 60)
    print("  BACKEND LOGIC TESTS (no keys / models / server required)")
    print("=" * 60)

    tests = [
        ("Env config defaults", test_env_defaults),
        ("Grounding coverage", test_grounding_coverage),
        ("Parsing F1", test_parsing_f1),
        ("API failure contract (malformed payload)", test_api_failure_contract),
        ("API failure contract (HTTP error)", test_api_http_error_contract),
    ]

    results = []
    for name, fn in tests:
        try:
            ok = fn()
        except Exception as exc:
            print(f"  {FAIL}  {name}: raised {type(exc).__name__}: {exc}")
            ok = False
        print(f"  {PASS if ok else FAIL}  {name}")
        results.append(ok)

    print()
    if all(results):
        print("  ALL TESTS PASSED")
        return 0

    failed = sum(1 for ok in results if not ok)
    print(f"  {failed} TEST(S) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
