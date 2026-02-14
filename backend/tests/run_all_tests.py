"""
Master Test Runner: Runs all backend tests in sequence.
Run from the backend directory:
  python tests/run_all_tests.py

Tests run in order:
  1. GPU & HuggingFace imports
  2. Pinecone connection & data
  3. LLM (Groq) connection
  4. API endpoints (requires server running)
"""

import subprocess
import sys
import os

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(TESTS_DIR)

tests = [
    ("GPU & HuggingFace Imports", "test_gpu_and_imports.py"),
    ("Pinecone Connection",       "test_pinecone.py"),
    ("LLM (Groq) Connection",     "test_llm.py"),
    ("API Endpoints",             "test_api_endpoints.py"),
    ("Prescription Pipeline",     "test_prescription_pipeline.py"),
]

def main():
    print("\n" + "=" * 60)
    print("  MEDICAL CHATBOT — BACKEND TEST SUITE")
    print("=" * 60)

    skip_api = "--skip-api" in sys.argv

    for name, script in tests:
        if skip_api and script == "test_api_endpoints.py":
            print(f"\n  ⏭  Skipping: {name} (--skip-api flag)")
            continue

        print(f"\n\n{'#' * 60}")
        print(f"  RUNNING: {name}")
        print(f"{'#' * 60}")

        result = subprocess.run(
            [sys.executable, os.path.join(TESTS_DIR, script)],
            cwd=BACKEND_DIR
        )

        if result.returncode != 0:
            print(f"\n  ⚠  Test '{name}' exited with code {result.returncode}")
            cont = input("  Continue with remaining tests? (y/n): ").strip().lower()
            if cont != "y":
                print("  Aborting test suite.")
                sys.exit(1)

    print(f"\n\n{'=' * 60}")
    print("  ALL TESTS COMPLETE")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
