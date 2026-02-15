"""
Evaluation Framework

Provides functions to evaluate the prescription pipeline:
- Parsing F1: Compare parsed JSON fields against ground truth
- API grounding coverage: % of drugs resolved in RxNorm/DailyMed
- Hallucination detection: Check if LLM answer contains unsupported claims

A hallucination is defined as:
- A claim about a disease not explicitly stated in prescription or API data
- A medication not present in parsed prescription
- A side effect not supported by DailyMed data
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="openai/gpt-oss-120b",
    temperature=0
)


# ==============================
# Parsing F1 Score
# ==============================

def _extract_field_set(data: dict) -> set[str]:
    """Recursively extract all non-null leaf values as strings for comparison."""
    values = set()

    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, dict):
            values.update(_extract_field_set(value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    values.update(_extract_field_set(item))
                elif item is not None:
                    values.add(str(item).lower().strip())
        else:
            values.add(str(value).lower().strip())

    return values


def compute_parsing_f1(predicted: dict, ground_truth: dict) -> dict:
    """
    Compute F1 score between predicted and ground truth prescription data.
    Compares all leaf-level field values.

    Returns:
        dict with precision, recall, f1, matched, predicted_count, truth_count
    """
    pred_values = _extract_field_set(predicted)
    truth_values = _extract_field_set(ground_truth)

    if not pred_values and not truth_values:
        return {
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
            "matched": 0,
            "predicted_count": 0,
            "truth_count": 0
        }

    matched = pred_values & truth_values

    precision = len(matched) / len(pred_values) if pred_values else 0.0
    recall = len(matched) / len(truth_values) if truth_values else 0.0
    f1 = (
        (2 * precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "matched": len(matched),
        "predicted_count": len(pred_values),
        "truth_count": len(truth_values)
    }


# ==============================
# API Grounding Coverage
# ==============================

def compute_grounding_coverage(api_results: list[dict]) -> dict:
    """
    Compute how well the medications are grounded in external APIs.

    Returns:
        dict with coverage_percent, grounded_count, total_count, details
    """
    if not api_results:
        return {
            "coverage_percent": 0.0,
            "grounded_count": 0,
            "total_count": 0,
            "details": []
        }

    details = []
    grounded = 0

    for result in api_results:
        drug = result.get("drug", "Unknown")
        has_rxnorm = result.get("rxnorm_id") is not None
        has_dailymed = result.get("dailymed_info") is not None
        is_grounded = has_rxnorm or has_dailymed

        if is_grounded:
            grounded += 1

        details.append({
            "drug": drug,
            "grounded": is_grounded,
            "rxnorm": has_rxnorm,
            "dailymed": has_dailymed
        })

    coverage = round((grounded / len(api_results)) * 100, 1)

    return {
        "coverage_percent": coverage,
        "grounded_count": grounded,
        "total_count": len(api_results),
        "details": details
    }


# ==============================
# Hallucination Detection
# ==============================

hallucination_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a medical fact-checking system.

Your job is to detect hallucinations in an AI-generated medical answer.

A hallucination is defined as:
1. A claim about a disease NOT explicitly stated in the prescription data
2. A medication NOT present in the parsed prescription
3. A side effect NOT supported by the provided DailyMed/API data
4. Any invented dosage, frequency, or clinical recommendation not in the source data

Analyze the answer against the source evidence and flag any unsupported claims.

Return valid JSON only.
"""),
    ("human",
     """Source prescription data:
{prescription_json}

Source API/drug data:
{api_data}

AI-generated answer to evaluate:
{answer}

Return JSON:
{{
  "hallucinations": [
    {{
      "claim": "The specific unsupported claim from the answer",
      "reason": "Why this is considered a hallucination",
      "severity": "High" | "Medium" | "Low"
    }}
  ],
  "hallucination_count": 0,
  "is_grounded": true,
  "grounding_notes": "Brief assessment of answer quality"
}}
""")
])


def detect_hallucinations(answer: str, prescription: dict, api_data: list) -> dict:
    """
    Detect hallucinations in an LLM-generated answer.

    Hallucination detection runs AFTER answer generation.
    Does not modify the answer, only flags risk.

    Returns:
        dict with hallucinations list, count, is_grounded flag, notes
    """
    if not answer or not answer.strip():
        return {
            "hallucinations": [],
            "hallucination_count": 0,
            "is_grounded": True,
            "grounding_notes": "No answer to evaluate"
        }

    try:
        logger.info("[Evaluation] Running hallucination detection...")

        formatted_prompt = hallucination_prompt.invoke({
            "prescription_json": json.dumps(prescription, indent=2),
            "api_data": json.dumps(api_data, indent=2) if api_data else "No API data available",
            "answer": answer
        })

        response = llm.invoke(formatted_prompt)
        raw_output = response.content.strip()

        # Strip markdown code fences if present
        if raw_output.startswith("```"):
            raw_output = raw_output.split("\n", 1)[-1]
            if raw_output.endswith("```"):
                raw_output = raw_output[:-3].strip()

        result = json.loads(raw_output)

        hallucination_count = result.get("hallucination_count", len(result.get("hallucinations", [])))

        logger.info(f"[Evaluation] Hallucinations found: {hallucination_count}")

        return {
            "hallucinations": result.get("hallucinations", []),
            "hallucination_count": hallucination_count,
            "is_grounded": result.get("is_grounded", hallucination_count == 0),
            "grounding_notes": result.get("grounding_notes", "")
        }

    except json.JSONDecodeError:
        logger.error("[Evaluation] Hallucination detector returned invalid JSON")
        return {
            "hallucinations": [],
            "hallucination_count": -1,
            "is_grounded": False,
            "grounding_notes": "Hallucination detection failed (invalid LLM output)"
        }

    except Exception:
        logger.exception("[Evaluation] Hallucination detection failed")
        return {
            "hallucinations": [],
            "hallucination_count": -1,
            "is_grounded": False,
            "grounding_notes": "Hallucination detection failed"
        }
