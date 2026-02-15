"""
Confidence Scoring Module

Computes confidence scores for each stage of the prescription pipeline:
- Diagnosis confidence (High/Medium/Low)
- Medication normalization confidence (per-drug RxNorm match)
- API grounding coverage (% of drugs grounded)

Overall confidence = min(stage_confidences)
"""

import re
from modules.medical_api import fetch_rxnorm_id, fetch_dailymed_summary
from logger import setup_logger

logger = setup_logger(__name__)

# ==============================
# Common medical abbreviations
# ==============================

KNOWN_ABBREVIATIONS = {
    "mbc", "cad", "dm", "htn", "ckd", "copd", "chf", "dvt",
    "pe", "uti", "acs", "mi", "cva", "tia", "gerd", "ibs",
    "ra", "oa", "sle", "ms", "tb", "hiv", "aids", "bph",
    "afib", "pvd", "pad", "ards", "ild", "nsclc", "sclc",
    "aml", "all", "cml", "cll", "dlbcl", "nhl", "hl",
}

CONFIDENCE_LEVELS = ["Low", "Medium", "High"]


# ==============================
# Diagnosis Confidence
# ==============================

def _score_diagnosis(diagnosis: str | None) -> dict:
    """
    High:   full explicit diagnosis text (e.g., "Metastatic Breast Cancer")
    Medium: abbreviation detected (e.g., "MBC")
    Low:    inferred only from medication pattern / missing
    """
    if not diagnosis or diagnosis.strip() == "":
        return {
            "level": "Low",
            "reason": "No diagnosis found in prescription"
        }

    text = diagnosis.strip()

    # Check if it's purely an abbreviation (all-caps, short, or known abbrev)
    tokens = re.findall(r'[A-Za-z]+', text)
    is_abbreviation = (
        len(tokens) <= 2
        and all(t.isupper() or t.lower() in KNOWN_ABBREVIATIONS for t in tokens)
    )

    if is_abbreviation:
        return {
            "level": "Medium",
            "reason": f"Abbreviation detected: \"{text}\""
        }

    # Full explicit text
    if len(text) > 5:
        return {
            "level": "High",
            "reason": "Full explicit diagnosis text"
        }

    return {
        "level": "Medium",
        "reason": f"Short diagnosis text: \"{text}\""
    }


# ==============================
# Medication Normalization Confidence
# ==============================

def _score_medications(medications: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Per-drug confidence based on RxNorm + DailyMed resolution.

    Returns:
        (medication_scores, api_results)
    """
    if not medications:
        return [], []

    scores = []
    api_results = []

    for med in medications:
        name = med.get("name", "")

        rx_id = fetch_rxnorm_id(name)
        dailymed = fetch_dailymed_summary(name)

        api_results.append({
            "drug": name,
            "rxnorm_id": rx_id,
            "dailymed_info": dailymed
        })

        if rx_id and dailymed:
            level = "High"
            reason = "Matched in RxNorm and DailyMed"
        elif rx_id or dailymed:
            level = "Medium"
            reason = f"Partial match (RxNorm: {'✓' if rx_id else '✗'}, DailyMed: {'✓' if dailymed else '✗'})"
        else:
            level = "Low"
            reason = "No match in RxNorm or DailyMed"

        scores.append({
            "name": name,
            "normalization": level,
            "rxnorm_match": rx_id is not None,
            "dailymed_match": dailymed is not None,
            "reason": reason
        })

    return scores, api_results


# ==============================
# API Grounding Coverage
# ==============================

def _compute_grounding_coverage(api_results: list[dict]) -> float:
    """
    Percentage of medications successfully grounded in external APIs.
    A drug is "grounded" if at least RxNorm OR DailyMed returned data.
    """
    if not api_results:
        return 0.0

    grounded = sum(
        1 for r in api_results
        if r.get("rxnorm_id") or r.get("dailymed_info")
    )

    return round((grounded / len(api_results)) * 100, 1)


# ==============================
# Overall Confidence
# ==============================

def _level_to_rank(level: str) -> int:
    return CONFIDENCE_LEVELS.index(level) if level in CONFIDENCE_LEVELS else 0


def _rank_to_level(rank: int) -> str:
    return CONFIDENCE_LEVELS[min(rank, len(CONFIDENCE_LEVELS) - 1)]


# ==============================
# Main Entry Point
# ==============================

def compute_confidence(prescription_data: dict) -> tuple[dict, list[dict]]:
    """
    Compute confidence scores for all stages of the prescription pipeline.

    Returns:
        (confidence_dict, api_results)
        api_results can be reused by interaction checker / answer chain.
    """
    logger.info("[Confidence] Computing confidence scores...")

    # 1. Diagnosis
    diagnosis_score = _score_diagnosis(
        prescription_data.get("diagnosis")
    )

    # 2. Medications
    medications = prescription_data.get("medications", []) or []
    med_scores, api_results = _score_medications(medications)

    # 3. API grounding
    grounding_coverage = _compute_grounding_coverage(api_results)

    # 4. Overall = min(stage confidences)
    all_levels = [diagnosis_score["level"]]
    all_levels += [s["normalization"] for s in med_scores]

    if all_levels:
        min_rank = min(_level_to_rank(l) for l in all_levels)
        overall = _rank_to_level(min_rank)
    else:
        overall = "Low"

    confidence = {
        "diagnosis_confidence": diagnosis_score["level"],
        "diagnosis_reason": diagnosis_score["reason"],
        "medication_scores": med_scores,
        "api_grounding_coverage": grounding_coverage,
        "overall_confidence": overall
    }

    logger.info(f"[Confidence] Overall: {overall}, Grounding: {grounding_coverage}%")

    return confidence, api_results
