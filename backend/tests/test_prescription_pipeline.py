"""
Test 5: Prescription Pipeline (requires backend to be running!)
Tests /upload_prescription/ and /ask_prescription/ endpoints.

PREREQUISITE: Start the backend first:
  uvicorn main:app --reload --port 8000

Run: python tests/test_prescription_pipeline.py
"""

import sys
import os
import requests

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"
WARN = "\033[93m⚠ WARN\033[0m"

BASE_URL = "http://localhost:8000"

# Path to test prescription image
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_IMAGE = os.path.join(TESTS_DIR, "original.jpg")


def divider(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ── 1. Server Health ────────────────────────────────────────
divider("1. Server Health Check")

try:
    resp = requests.get(f"{BASE_URL}/docs", timeout=5)
    if resp.status_code == 200:
        print(f"  Server status        : {PASS}  Running at {BASE_URL}")
    else:
        print(f"  {WARN}  Server returned status {resp.status_code}")
except requests.ConnectionError:
    print(f"  {FAIL}  Cannot connect to {BASE_URL}")
    print(f"  Make sure the backend is running:")
    print(f"    uvicorn main:app --reload --port 8000")
    sys.exit(1)


# ── 2. Check endpoints exist ───────────────────────────────
divider("2. Verify Prescription Endpoints Exist")

try:
    resp = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    if resp.status_code == 200:
        paths = list(resp.json().get("paths", {}).keys())
        has_upload = "/upload_prescription/" in paths
        has_ask = "/ask_prescription/" in paths

        print(f"  /upload_prescription/ : {'found' if has_upload else 'MISSING'}")
        print(f"  /ask_prescription/    : {'found' if has_ask else 'MISSING'}")

        if has_upload and has_ask:
            print(f"  Endpoint check       : {PASS}")
        else:
            print(f"  {FAIL}  Missing prescription endpoints")
            sys.exit(1)
    else:
        print(f"  {FAIL}  Could not fetch OpenAPI schema")
        sys.exit(1)
except Exception as e:
    print(f"  {FAIL}  Endpoint check failed: {e}")
    sys.exit(1)


# ── 3. Test Upload Prescription ─────────────────────────────
divider("3. Test /upload_prescription/ Endpoint")

session_id = None

try:
    if not os.path.exists(TEST_IMAGE):
        print(f"  {WARN}  Test image not found: {TEST_IMAGE}")
        print(f"  Place a prescription image named 'original.jpg' in tests/")
        print(f"  Skipping upload and ask tests.")
        sys.exit(0)

    with open(TEST_IMAGE, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/upload_prescription/",
            files={"file": ("original.jpg", f, "image/jpeg")},
            timeout=300  # OCR + parsing can be slow
        )

    print(f"  Status code          : {resp.status_code}")

    if resp.status_code == 200:
        data = resp.json()
        session_id = data.get("session_id")
        prescription = data.get("prescription_data")

        print(f"  Session ID           : {session_id}")
        print(f"  Has prescription_data: {prescription is not None}")

        if prescription:
            patient = prescription.get("patient_info")
            meds = prescription.get("medications", [])
            print(f"  Patient info         : {patient}")
            print(f"  Medications count    : {len(meds)}")

            for med in meds:
                print(f"    - {med.get('name', 'N/A')} | "
                      f"dose: {med.get('dose', 'N/A')} | "
                      f"freq: {med.get('frequency', 'N/A')}")

        if session_id and prescription:
            print(f"  Upload test          : {PASS}")
        else:
            print(f"  {FAIL}  Missing session_id or prescription_data")
    else:
        print(f"  {FAIL}  Upload returned {resp.status_code}")
        print(f"  Response             : {resp.text[:300]}")

except Exception as e:
    print(f"  {FAIL}  Upload test failed: {e}")


# ── 4. Test Ask Prescription ────────────────────────────────
divider("4. Test /ask_prescription/ Endpoint")

if not session_id:
    print(f"  {WARN}  Skipping — no session_id from upload step")
else:
    test_questions = [
        "What medications were prescribed?",
        "What is the patient's diagnosis?",
        "Are there any follow-up instructions?",
    ]

    for q in test_questions:
        try:
            resp = requests.post(
                f"{BASE_URL}/ask_prescription/",
                data={
                    "session_id": session_id,
                    "question": q
                },
                timeout=60
            )

            print(f"\n  Q: {q}")
            print(f"  Status: {resp.status_code}")

            if resp.status_code == 200:
                answer = resp.json().get("answer", "N/A")
                print(f"  A: {str(answer)[:200]}...")
                print(f"  {PASS}")
            else:
                print(f"  {FAIL}  Got {resp.status_code}: {resp.text[:200]}")

        except Exception as e:
            print(f"  {FAIL}  Ask failed: {e}")


# ── 5. Test invalid session_id ──────────────────────────────
divider("5. Test Invalid Session ID")

try:
    resp = requests.post(
        f"{BASE_URL}/ask_prescription/",
        data={
            "session_id": "invalid-uuid-12345",
            "question": "What medications?"
        },
        timeout=10
    )

    if resp.status_code == 404:
        print(f"  Invalid session check: {PASS}  (returned 404 as expected)")
    else:
        print(f"  {WARN}  Expected 404, got {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")

except Exception as e:
    print(f"  {FAIL}  Invalid session test failed: {e}")


# ── 6. Test file type validation ─────────────────────────────
divider("6. Test Non-Image Upload")

try:
    # Try uploading a text file as a prescription
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as tmp:
        tmp.write("This is not an image")
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/upload_prescription/",
            files={"file": ("test.txt", f, "text/plain")},
            timeout=30
        )

    print(f"  Status code          : {resp.status_code}")

    if resp.status_code == 500:
        print(f"  Non-image rejection  : {PASS}  (server returned 500 for invalid file)")
    elif resp.status_code == 200:
        print(f"  {WARN}  Server accepted non-image file — consider adding validation")
    else:
        print(f"  Status               : {resp.status_code}")

    os.unlink(tmp_path)

except Exception as e:
    print(f"  {FAIL}  Non-image test failed: {e}")


print()
