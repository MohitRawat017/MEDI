"""
Test 4: API Endpoints (requires backend to be running!)
Tests /upload_pdfs/ and /ask/ endpoints via HTTP requests.

PREREQUISITE: Start the backend first:
  uvicorn main:app --reload --port 8000

Run: python tests/test_api_endpoints.py
"""

import sys
import os
import requests
import tempfile

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"
WARN = "\033[93m⚠ WARN\033[0m"

BASE_URL = "http://localhost:8000"

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


# ── 2. Test Upload Endpoint ─────────────────────────────────
divider("2. Test /upload_pdfs/ Endpoint")

try:
    # Create a minimal valid PDF for testing
    from reportlab.pdfgen import canvas as pdf_canvas

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    c = pdf_canvas.Canvas(tmp_path)
    c.drawString(72, 720, "This is a test PDF for the Medical Chatbot.")
    c.drawString(72, 700, "Diabetes is a chronic metabolic condition.")
    c.drawString(72, 680, "Symptoms include increased thirst and frequent urination.")
    c.save()

    with open(tmp_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/upload_pdfs/",
            files={"files": ("test_medical.pdf", f, "application/pdf")},
            data={"namespace": "default"},
            timeout=120
        )

    print(f"  Status code          : {resp.status_code}")
    print(f"  Response             : {resp.json()}")

    if resp.status_code == 200:
        print(f"  Upload test          : {PASS}")
    else:
        print(f"  {FAIL}  Upload returned {resp.status_code}")

    os.unlink(tmp_path)

except ImportError:
    print(f"  {WARN}  reportlab not installed — skipping PDF creation test")
    print(f"  Install with: pip install reportlab")
    print(f"  Or test manually by uploading a PDF via the frontend")

except Exception as e:
    print(f"  {FAIL}  Upload test failed: {e}")


# ── 3. Test Ask Endpoint ────────────────────────────────────
divider("3. Test /ask/ Endpoint")

try:
    resp = requests.post(
        f"{BASE_URL}/ask/",
        data={
            "question": "What is diabetes?",
            "namespace": "default"
        },
        timeout=60
    )

    print(f"  Status code          : {resp.status_code}")
    data = resp.json()
    print(f"  Response             : {str(data.get('response', 'N/A'))[:150]}...")
    print(f"  Sources              : {data.get('source', [])}")

    if resp.status_code == 200 and data.get("response"):
        if "couldn't find" in data["response"].lower() or "sorry" in data["response"].lower():
            print(f"  {WARN}  Got fallback response — vectorstore may be empty for this namespace")
        else:
            print(f"  Ask test             : {PASS}")
    else:
        print(f"  {FAIL}  Ask returned unexpected response")

except Exception as e:
    print(f"  {FAIL}  Ask test failed: {e}")


# ── 4. Test OpenAPI docs ────────────────────────────────────
divider("4. OpenAPI Documentation")

try:
    resp = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    if resp.status_code == 200:
        api_info = resp.json()
        paths = list(api_info.get("paths", {}).keys())
        print(f"  Title                : {api_info.get('info', {}).get('title', 'N/A')}")
        print(f"  Endpoints            : {paths}")
        print(f"  OpenAPI docs         : {PASS}")
    else:
        print(f"  {WARN}  OpenAPI returned {resp.status_code}")
except Exception as e:
    print(f"  {FAIL}  OpenAPI test failed: {e}")

print()
