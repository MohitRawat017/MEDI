"""
Drug Interaction Checker

Interaction detection is advisory only.
LLM-generated interaction assessments must not be treated as definitive medical advice.

Two-layer approach:
1. RxNorm drug class lookup (pharmacological classes via RxClass API)
2. LLM-based interaction analysis with structured output

Since the RxNorm Interaction API was discontinued (Jan 2024), we use
drug class overlap + LLM reasoning + OpenFDA adverse event signals.
"""

import os
import json
from itertools import combinations
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from modules.medical_api import fetch_drug_classes, fetch_openfda_interactions
from logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ==============================
# LLM for interaction analysis
# ==============================

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="openai/gpt-oss-120b",
    temperature=0
)

interaction_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a clinical pharmacology assistant.

You analyze potential drug-drug interactions based on:
1. Drug pharmacological classes
2. Known adverse event signals from FDA reports
3. Your medical knowledge

For each drug pair, assess:
- Whether a clinically significant interaction exists
- Risk level: "High", "Moderate", or "Low"
- Brief clinical description of the interaction
- A recommendation for the prescriber

IMPORTANT:
- Only flag interactions with real clinical significance
- If no interaction is known, do NOT invent one
- Return valid JSON only
- This is advisory only, not definitive medical advice
"""),
    ("human",
     """Analyze drug-drug interactions for these medications:

Medications: {medications}

Drug class data:
{drug_classes}

FDA adverse event signals:
{fda_signals}

Return JSON:
{{
  "interactions": [
    {{
      "drug_pair": ["DrugA", "DrugB"],
      "risk_level": "High" | "Moderate" | "Low",
      "description": "...",
      "recommendation": "..."
    }}
  ],
  "summary": "Brief overall assessment"
}}

If no interactions found, return: {{"interactions": [], "summary": "No significant interactions detected"}}
""")
])


# ==============================
# Main Interaction Checker
# ==============================

def check_interactions(medications: list[dict]) -> dict:
    """
    Check for drug-drug interactions among prescribed medications.

    Interaction detection is advisory only.
    LLM-generated interaction assessments must not be treated
    as definitive medical advice.

    Args:
        medications: list of medication dicts with at least "name" key

    Returns:
        dict with interactions, total_checked, interactions_found, disclaimer
    """
    if not medications or len(medications) < 2:
        return {
            "interactions": [],
            "total_checked": len(medications) if medications else 0,
            "interactions_found": 0,
            "disclaimer": "Interaction detection is advisory only."
        }

    med_names = [m.get("name", "") for m in medications if m.get("name")]

    if len(med_names) < 2:
        return {
            "interactions": [],
            "total_checked": len(med_names),
            "interactions_found": 0,
            "disclaimer": "Interaction detection is advisory only."
        }

    logger.info(f"[Interactions] Checking {len(med_names)} medications: {med_names}")

    # Layer 1: Fetch drug classes for context
    drug_classes = {}
    for name in med_names:
        classes = fetch_drug_classes(name)
        drug_classes[name] = classes if classes else ["Unknown"]

    # Layer 2: Fetch FDA adverse event signals
    fda_signals = {}
    for name in med_names:
        signals = fetch_openfda_interactions(name)
        if signals:
            fda_signals[name] = signals

    # Layer 3: LLM-based interaction analysis
    try:
        formatted_prompt = interaction_prompt.invoke({
            "medications": json.dumps(med_names),
            "drug_classes": json.dumps(drug_classes, indent=2),
            "fda_signals": json.dumps(fda_signals, indent=2) if fda_signals else "No FDA signals found"
        })

        response = llm.invoke(formatted_prompt)
        raw_output = response.content.strip()

        # Strip markdown code fences if present
        if raw_output.startswith("```"):
            raw_output = raw_output.split("\n", 1)[-1]
            if raw_output.endswith("```"):
                raw_output = raw_output[:-3].strip()

        result = json.loads(raw_output)

        interactions = result.get("interactions", [])
        total_pairs = len(list(combinations(med_names, 2)))

        logger.info(f"[Interactions] Found {len(interactions)} interactions out of {total_pairs} pairs")

        return {
            "interactions": interactions,
            "total_checked": total_pairs,
            "interactions_found": len(interactions),
            "summary": result.get("summary", ""),
            "drug_classes": drug_classes,
            "disclaimer": "Interaction detection is advisory only. Do not treat as definitive medical advice."
        }

    except json.JSONDecodeError:
        logger.error("[Interactions] LLM returned invalid JSON")
        return {
            "interactions": [],
            "total_checked": len(list(combinations(med_names, 2))),
            "interactions_found": 0,
            "error": "Failed to parse interaction analysis",
            "disclaimer": "Interaction detection is advisory only."
        }

    except Exception:
        logger.exception("[Interactions] Unexpected error during interaction check")
        return {
            "interactions": [],
            "total_checked": 0,
            "interactions_found": 0,
            "error": "Interaction check failed",
            "disclaimer": "Interaction detection is advisory only."
        }
