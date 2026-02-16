"""
Test: OCR Engine Comparative Evaluation
========================================
Runs both LightOnOCR and GLM-OCR against 6 prescription images, then uses
Groq (gpt-oss-120b) to score each output against the human-validated
ground truth in validation.md.

Metrics computed:
  Text-level   – CER, WER, Layout Preservation
  Entity-level – Medication Detection Recall, Numeric Dosage Accuracy,
                 Drug Extraction Accuracy, Dose Extraction Accuracy,
                 Date Extraction Accuracy, Structured JSON F1

Run:
    cd backend
    python tests/test_ocr_evaluation.py
"""

import os
import sys
import json
import re
import unicodedata
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

# ── path setup ──────────────────────────────────────────────
TESTS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TESTS_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from modules.ocr import extract_text_from_image  # noqa: E402

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── Groq client (langchain) ────────────────────────────────
from langchain_groq import ChatGroq  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402

evaluator_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="openai/gpt-oss-120b",
    temperature=0,
)


# =====================================================
# 1.  GROUND-TRUTH DATA (from validation.md)
# =====================================================
# Each entry maps a prescription tag to its image filename
# and the validated reference text + structured fields.
# =====================================================

GROUND_TRUTH: Dict[str, dict] = {
    "DOD": {
        "image": str(TESTS_DIR / "DOD.png"),
        "reference_text": (
            "DD Form 1289\n1 NOV 71\nDOD PRESCRIPTION\n"
            "Patient\nJohn R. Doe, HM3, USN\nU.S.S. Neverforgotten (DD 178)\n"
            "Medical Facility\nU.S.S. Neverforgotten (DD 178)\n"
            "Date\n23 Jan 99\n"
            "℞ Prescription\nInscription\nTr. Belladonna — 15 mL\n"
            "Amphogel q.s. ad — 120 mL\nSubscription\nM. et Ft solution\n"
            "Signa\nSig: 5 mL t.i.d. a.c.\n"
            "Manufacturer\nWyeth\nLot No\nP39K106\nExpiration Date\n12/02\n"
            "Filled By\nKMT\nRx Number\n10072\n"
            "Prescriber\nJack R. Frost\nLCDR, MD, USNR"
        ),
        "drugs": ["Tr. Belladonna", "Amphogel"],
        "doses": ["15 mL", "120 mL", "5 mL"],
        "dates": ["23 Jan 99", "1 NOV 71", "12/02"],
        "structured": {
            "patient_name": "John R. Doe",
            "prescriber": "Jack R. Frost",
            "medications": [
                {"name": "Tr. Belladonna", "dose": "15 mL"},
                {"name": "Amphogel", "dose": "120 mL"},
            ],
        },
    },
    "TALAT": {
        "image": str(TESTS_DIR / "TALAT.jpg"),
        "reference_text": (
            "Dr. Talat Aziz\nM.B.B.S (Delhi)\n"
            "1430, Qasimjan Street, Ballimaran, Delhi-110006\n"
            "Tel: 23928493\nEmail: azizclinic@hotmail.com\nMob: 9899874855\n"
            "Date\n18-8-18\n"
            "Medical certificate\n"
            "This is to certify that Ms. Sheeba Malik, whose signatures is given below, "
            "is a follow-up case of Sciatica with Prolapse disc and is under my care.\n"
            "I advise her complete bed rest for 3 months i.e. from 18-8-18 to 18-11-18.\n"
            "Signature:\nSheeba\n"
            "Signed:\nDr. Talat Aziz\nRegd. No. MCI 4809"
        ),
        "drugs": [],
        "doses": [],
        "dates": ["18-8-18", "18-11-18"],
        "structured": {
            "patient_name": "Sheeba Malik",
            "prescriber": "Dr. Talat Aziz",
            "medications": [],
        },
    },
    "ASHOK": {
        "image": str(TESTS_DIR / "ASHOK.png"),
        "reference_text": (
            "Dr. Ashok Gupta\nM.B.B.S., M.D. (Bal Rog Visheshagya)\n"
            "Reg. No. 32286\nDate\n04 Nov 2019\n"
            "Patient\nR/o Govind Puri\n"
            "Medications\nSyp. Sinmol DS — 4 mL SOS\n"
            "Syp. Mucolite LS — 2.5 mL tds\n"
            "Tab. Meftal-P — 1 tab SOS\n"
            "Review\n07 Nov 2019\nTab. as advised × 5 days"
        ),
        "drugs": ["Sinmol DS", "Mucolite LS", "Meftal-P"],
        "doses": ["4 mL", "2.5 mL", "1 tab"],
        "dates": ["04 Nov 2019", "07 Nov 2019"],
        "structured": {
            "patient_name": None,
            "prescriber": "Dr. Ashok Gupta",
            "medications": [
                {"name": "Sinmol DS", "dose": "4 mL", "frequency": "SOS"},
                {"name": "Mucolite LS", "dose": "2.5 mL", "frequency": "tds"},
                {"name": "Meftal-P", "dose": "1 tab", "frequency": "SOS"},
            ],
        },
    },
    "SANJEEV": {
        "image": str(TESTS_DIR / "SANJEEV.webp"),
        "reference_text": (
            "Dr. Sanjeev Kumar Sharma\nM.B.B.S., M.D. (Ped.)\n"
            "CMO Regd. No. 2093/2623\nDate\n11/11/19\n"
            "Patient\nAarav\nAge: 1 year\n"
            "Medications\n"
            "A. Cef-P — 5 mL 10 days\n"
            "A. Eklo-P — 5 mL BD\n"
            "A. Alb M — 5 mL\n"
            "A. Renzyo — 100 5 mL 2x\n"
            "Nebulization:\n"
            "Asthalin 2 mL + Budecort 2 mL BD\n"
            "By Duolin 2 mL in NS"
        ),
        "drugs": ["Cef-P", "Eklo-P", "Alb M", "Renzyo", "Asthalin", "Budecort", "Duolin"],
        "doses": ["5 mL", "5 mL", "5 mL", "5 mL", "2 mL", "2 mL", "2 mL"],
        "dates": ["11/11/19"],
        "structured": {
            "patient_name": "Aarav",
            "prescriber": "Dr. Sanjeev Kumar Sharma",
            "medications": [
                {"name": "Cef-P", "dose": "5 mL", "duration": "10 days"},
                {"name": "Eklo-P", "dose": "5 mL", "frequency": "BD"},
                {"name": "Alb M", "dose": "5 mL"},
                {"name": "Renzyo", "dose": "5 mL"},
                {"name": "Asthalin", "dose": "2 mL", "frequency": "BD"},
                {"name": "Budecort", "dose": "2 mL", "frequency": "BD"},
                {"name": "Duolin", "dose": "2 mL"},
            ],
        },
    },
    "BAKER": {
        "image": str(TESTS_DIR / "BAKER.jpg"),
        "reference_text": (
            "Dr. W. P. Baker\nPhysician and Surgeon\nHillman City, Seattle\n"
            "℞ Sick headache\n"
            "Ext. Cannabis Ind. — gr IV\n"
            "Croton chloral — gr XV\n"
            "Ft. caps. no XVI\n"
            "Sig: Give one tablet every ½ hour"
        ),
        "drugs": ["Ext. Cannabis Ind.", "Croton chloral"],
        "doses": ["gr IV", "gr XV"],
        "dates": [],
        "structured": {
            "patient_name": None,
            "prescriber": "Dr. W. P. Baker",
            "medications": [
                {"name": "Ext. Cannabis Ind.", "dose": "gr IV"},
                {"name": "Croton chloral", "dose": "gr XV"},
            ],
        },
    },
    "ORIGINAL": {
        "image": str(TESTS_DIR / "original.jpg"),
        "reference_text": (
            "Netaji Subhas Chandra Bose Cancer Hospital\n"
            "3081 Nayabad, Kolkata - 700 094\n"
            "Patient\nDalia Kundu\nMR No: NCRI/21/1427\nSex: F\nAge: 64\n"
            "Appointment Date: 10-02-2021\n"
            "Clinical Notes\nMBC\n(8/5/3)\n(Bone / Lung / Liver)\n"
            "Diagnosis:\n2D Echo - (n)\n"
            "Medicine Prescribed\nPlan:\nG# (P+H)\nInj. Xgeva — 120\n"
            "Advice\nAdv on D6\nHMW — TDS\nCloscu — TDS\n"
            "Follow-Up\nT. Dora — BD D2-D4\nT. Ondan — BD D2-D4\n"
            "T. Ultracet — BD × 5 days\n"
            "Consultant:\nTanmoy Kumar Mandal\nRegn No: WBMC-63430"
        ),
        "drugs": ["Xgeva", "Dora", "Ondan", "Ultracet", "HMW", "Closcu"],
        "doses": ["120"],
        "dates": ["10-02-2021"],
        "structured": {
            "patient_name": "Dalia Kundu",
            "prescriber": "Tanmoy Kumar Mandal",
            "medications": [
                {"name": "Xgeva", "dose": "120"},
                {"name": "Dora", "frequency": "BD", "duration": "D2-D4"},
                {"name": "Ondan", "frequency": "BD", "duration": "D2-D4"},
                {"name": "Ultracet", "frequency": "BD", "duration": "5 days"},
            ],
        },
    },
}


# =====================================================
# 2.  TEXT NORMALISATION HELPERS
# =====================================================

def normalise(text: str) -> str:
    """Lower-case, collapse whitespace, strip accents / special chars."""
    text = unicodedata.normalize("NFKD", text)
    text = text.lower().strip()
    text = re.sub(r"[^\w\s.,;:/()\-]", "", text)  # keep basic punctuation
    text = re.sub(r"\s+", " ", text)
    return text


def tokenise(text: str) -> List[str]:
    return normalise(text).split()


# =====================================================
# 3.  METRIC COMPUTATION (text-level)
# =====================================================

def _levenshtein(a: str, b: str) -> int:
    """Character-level Levenshtein distance."""
    n, m = len(a), len(b)
    dp = list(range(m + 1))
    for i in range(1, n + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            ins = dp[j] + 1
            dele = dp[j - 1] + 1
            sub = prev + cost
            prev = dp[j]
            dp[j] = min(ins, dele, sub)
    return dp[m]


def compute_cer(ocr: str, ref: str) -> float:
    """Character Error Rate = edit_distance / len(reference)."""
    a, b = normalise(ocr), normalise(ref)
    if not b:
        return 0.0
    return _levenshtein(a, b) / len(b)


def compute_wer(ocr: str, ref: str) -> float:
    """Word Error Rate (token-level Levenshtein)."""
    hyp_tokens = tokenise(ocr)
    ref_tokens = tokenise(ref)
    if not ref_tokens:
        return 0.0
    return _levenshtein(" ".join(hyp_tokens), " ".join(ref_tokens)) / len(" ".join(ref_tokens))


def _word_level_levenshtein(a: List[str], b: List[str]) -> int:
    """Word-level Levenshtein distance."""
    n, m = len(a), len(b)
    dp = list(range(m + 1))
    for i in range(1, n + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            ins = dp[j] + 1
            dele = dp[j - 1] + 1
            sub = prev + cost
            prev = dp[j]
            dp[j] = min(ins, dele, sub)
    return dp[m]


def compute_wer_proper(ocr: str, ref: str) -> float:
    """Proper word-level WER = word_edit_distance / len(ref_words)."""
    hyp_tokens = tokenise(ocr)
    ref_tokens = tokenise(ref)
    if not ref_tokens:
        return 0.0
    return _word_level_levenshtein(hyp_tokens, ref_tokens) / len(ref_tokens)


# =====================================================
# 4.  ENTITY-LEVEL METRICS (fuzzy matching)
# =====================================================

def _fuzzy_match(candidate: str, reference: str, threshold: float = 0.6) -> bool:
    """Return True if normalised candidate is close enough to reference."""
    c, r = normalise(candidate), normalise(reference)
    if r in c or c in r:
        return True
    dist = _levenshtein(c, r)
    max_len = max(len(c), len(r), 1)
    return (1 - dist / max_len) >= threshold


def recall_set(ocr_text: str, ground_items: List[str]) -> float:
    """Fraction of ground-truth items found (fuzzy) in OCR text."""
    if not ground_items:
        return 1.0  # nothing to find → perfect
    found = sum(1 for item in ground_items if _fuzzy_match(ocr_text, item))
    return found / len(ground_items)


def drug_extraction_accuracy(ocr_text: str, drugs: List[str]) -> float:
    return recall_set(ocr_text, drugs)


def dose_extraction_accuracy(ocr_text: str, doses: List[str]) -> float:
    return recall_set(ocr_text, doses)


def date_extraction_accuracy(ocr_text: str, dates: List[str]) -> float:
    return recall_set(ocr_text, dates)


def medication_detection_recall(ocr_text: str, drugs: List[str]) -> float:
    return drug_extraction_accuracy(ocr_text, drugs)


def numeric_dosage_accuracy(ocr_text: str, doses: List[str]) -> float:
    """Check numeric part of doses (e.g. '15' from '15 mL')."""
    if not doses:
        return 1.0
    nums = []
    for d in doses:
        m = re.search(r"[\d.]+", d)
        if m:
            nums.append(m.group())
    if not nums:
        return 1.0
    found = sum(1 for n in nums if n in ocr_text)
    return found / len(nums)


# =====================================================
# 5.  LAYOUT PRESERVATION (heuristic line-based)
# =====================================================

def layout_preservation_score(ocr_text: str, ref_text: str) -> float:
    """
    Heuristic: fraction of reference lines whose key content appears
    in the OCR output (order-aware, normalised).
    """
    ref_lines = [normalise(l) for l in ref_text.strip().splitlines() if l.strip()]
    if not ref_lines:
        return 1.0
    ocr_norm = normalise(ocr_text)
    found = 0
    for line in ref_lines:
        # check if most words of the line appear in OCR
        words = line.split()
        if not words:
            found += 1
            continue
        matched = sum(1 for w in words if w in ocr_norm)
        if matched / len(words) >= 0.5:
            found += 1
    return found / len(ref_lines)


# =====================================================
# 6.  STRUCTURED JSON F1  via Groq LLM
# =====================================================

STRUCTURED_EVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     """You are a strict medical data extraction evaluator.

Given:
  - GROUND TRUTH structured JSON (the correct answer)
  - OCR TEXT (raw output from an OCR engine)

Tasks:
1. From the OCR TEXT, try to extract the same structured fields as in
   the ground truth (patient_name, prescriber, medications list with
   name, dose, frequency, duration).
2. Compare the extracted fields with the ground truth.
3. Compute Precision, Recall, F1 for the medications list
   (match by drug name — fuzzy match allowed).
4. Report field-level accuracy for patient_name, prescriber, dates.

Return ONLY valid JSON with this schema:
{{
  "extracted_patient_name": string | null,
  "extracted_prescriber": string | null,
  "extracted_medications": [
    {{"name": string, "dose": string|null, "frequency": string|null, "duration": string|null}}
  ],
  "patient_name_correct": boolean,
  "prescriber_correct": boolean,
  "med_precision": float,
  "med_recall": float,
  "med_f1": float,
  "field_level_notes": string
}}

Be lenient with minor spelling variations or abbreviation differences
(e.g. "Dr." vs "Dr", trailing periods, etc.), but strict on actual
content mismatches.
"""),
    ("human",
     """GROUND TRUTH JSON:
{ground_truth}

OCR TEXT:
{ocr_text}

Evaluate and return JSON only."""),
])


def evaluate_structured_json_f1(ocr_text: str, gt_structured: dict) -> dict:
    """Use Groq LLM to compute structured extraction F1."""
    try:
        formatted = STRUCTURED_EVAL_PROMPT.invoke({
            "ground_truth": json.dumps(gt_structured, indent=2),
            "ocr_text": ocr_text,
        })
        response = evaluator_llm.invoke(formatted)
        raw = response.content.strip()
        # Try to extract JSON from response
        json_match = re.search(r"\{[\s\S]*\}", raw)
        if json_match:
            return json.loads(json_match.group())
        return {"error": "No JSON in LLM response", "raw": raw[:500]}
    except Exception as e:
        return {"error": str(e)}


# =====================================================
# 7.  RESULT DATACLASS
# =====================================================

@dataclass
class PrescriptionResult:
    name: str
    engine: str
    cer: float = 0.0
    wer: float = 0.0
    layout_score: float = 0.0
    medication_recall: float = 0.0
    numeric_dosage_acc: float = 0.0
    drug_acc: float = 0.0
    dose_acc: float = 0.0
    date_acc: float = 0.0
    structured_f1: float = 0.0
    structured_detail: dict = field(default_factory=dict)
    ocr_text: str = ""


# =====================================================
# 8.  MAIN EVALUATION LOOP
# =====================================================

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"


def divider(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def run_evaluation(engines: Optional[List[str]] = None):
    if engines is None:
        engines = ["lighton", "glm"]

    all_results: List[PrescriptionResult] = []

    for engine in engines:
        divider(f"ENGINE: {engine.upper()}")

        for tag, gt in GROUND_TRUTH.items():
            image_path = gt["image"]
            if not os.path.exists(image_path):
                print(f"  {FAIL} {tag}: image not found at {image_path}")
                continue

            print(f"\n  ── {tag} ({os.path.basename(image_path)}) ──")

            # --- Run OCR ---
            try:
                ocr_text = extract_text_from_image(image_path, engine=engine)
            except Exception as e:
                print(f"  {FAIL} OCR failed: {e}")
                all_results.append(PrescriptionResult(name=tag, engine=engine))
                continue

            print(f"  OCR length: {len(ocr_text)} chars")

            # --- Text metrics ---
            cer = compute_cer(ocr_text, gt["reference_text"])
            wer = compute_wer_proper(ocr_text, gt["reference_text"])
            layout = layout_preservation_score(ocr_text, gt["reference_text"])
            med_recall = medication_detection_recall(ocr_text, gt["drugs"])
            num_dose = numeric_dosage_accuracy(ocr_text, gt["doses"])
            drug_acc = drug_extraction_accuracy(ocr_text, gt["drugs"])
            dose_acc = dose_extraction_accuracy(ocr_text, gt["doses"])
            date_acc = date_extraction_accuracy(ocr_text, gt["dates"])

            print(f"  CER              : {cer:.4f}")
            print(f"  WER              : {wer:.4f}")
            print(f"  Layout Score     : {layout:.4f}")
            print(f"  Medication Recall: {med_recall:.4f}")
            print(f"  Numeric Dosage   : {num_dose:.4f}")
            print(f"  Drug Accuracy    : {drug_acc:.4f}")
            print(f"  Dose Accuracy    : {dose_acc:.4f}")
            print(f"  Date Accuracy    : {date_acc:.4f}")

            # --- Structured JSON F1 via LLM ---
            struct_result = evaluate_structured_json_f1(ocr_text, gt["structured"])
            struct_f1 = struct_result.get("med_f1", 0.0)
            if isinstance(struct_f1, (int, float)):
                pass
            else:
                struct_f1 = 0.0

            print(f"  Structured F1    : {struct_f1:.4f}")
            if struct_result.get("field_level_notes"):
                print(f"  Notes            : {struct_result['field_level_notes'][:120]}")

            result = PrescriptionResult(
                name=tag,
                engine=engine,
                cer=cer,
                wer=wer,
                layout_score=layout,
                medication_recall=med_recall,
                numeric_dosage_acc=num_dose,
                drug_acc=drug_acc,
                dose_acc=dose_acc,
                date_acc=date_acc,
                structured_f1=struct_f1,
                structured_detail=struct_result,
                ocr_text=ocr_text[:500],
            )
            all_results.append(result)

    # ── Summary ─────────────────────────────────────────────
    divider("SUMMARY COMPARISON")
    for engine in engines:
        engine_results = [r for r in all_results if r.engine == engine]
        if not engine_results:
            continue

        n = len(engine_results)
        avg = lambda attr: sum(getattr(r, attr) for r in engine_results) / n

        print(f"\n  {BOLD}{engine.upper()}{RESET}  ({n} prescriptions)")
        print(f"    Avg CER              : {avg('cer'):.4f}")
        print(f"    Avg WER              : {avg('wer'):.4f}")
        print(f"    Avg Layout Score     : {avg('layout_score'):.4f}")
        print(f"    Avg Medication Recall: {avg('medication_recall'):.4f}")
        print(f"    Avg Numeric Dosage   : {avg('numeric_dosage_acc'):.4f}")
        print(f"    Avg Drug Accuracy    : {avg('drug_acc'):.4f}")
        print(f"    Avg Dose Accuracy    : {avg('dose_acc'):.4f}")
        print(f"    Avg Date Accuracy    : {avg('date_acc'):.4f}")
        print(f"    Avg Structured F1    : {avg('structured_f1'):.4f}")

    # ── Save detailed JSON report ───────────────────────────
    report_path = TESTS_DIR / "ocr_evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in all_results], f, indent=2, ensure_ascii=False)
    print(f"\n  Detailed report saved to: {report_path}")

    return all_results


# =====================================================
# 9.  CLI ENTRY POINT
# =====================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OCR Engine Comparative Evaluation")
    parser.add_argument(
        "--engine",
        choices=["lighton", "glm", "both"],
        default="both",
        help="Which OCR engine(s) to evaluate (default: both)",
    )
    args = parser.parse_args()

    if args.engine == "both":
        engines = ["glm", "lighton"]
    else:
        engines = [args.engine]

    run_evaluation(engines=engines)
