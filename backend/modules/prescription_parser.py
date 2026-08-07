import json
from typing import List, Optional
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from logger import setup_logger
from modules.llm import GPT_OSS_120B, get_chat_groq

logger = setup_logger(__name__)


# ==============================
# Structured Schema Definition
# ==============================

class PatientInfo(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    mr_no: Optional[str] = None
    appointment_date: Optional[str] = None


class Medication(BaseModel):
    name: str
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None


class PrescriptionData(BaseModel):
    patient_info: Optional[PatientInfo] = None
    diagnosis: Optional[str] = None
    clinical_notes: Optional[str] = None
    medications: Optional[List[Medication]] = None
    advice: Optional[List[str]] = None
    follow_up: Optional[List[str]] = None


prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a medical prescription parsing system.

Tasks:
1. Extract structured data.
2. Correct OCR errors in medical terms and drug names.
3. Standardize drug names to their common generic form when possible.
4. Remove meaningless tokens or single-letter noise.
5. Do not invent information.
6. If uncertain, keep original word.
7. If you are uncertain about a drug name, do NOT guess. Keep the original OCR word.

Return only valid JSON.
"""),
    ("human",
     """OCR TEXT:

{ocr_text}

Return JSON with this format:

{{
  "patient_info": {{
    "name": string | null,
    "age": integer | null,
    "sex": string | null,
    "mr_no": string | null,
    "appointment_date": string | null
  }},
  "diagnosis": string | null,
  "clinical_notes": string | null,
  "medications": [
    {{
      "name": string,
      "dose": string | null,
      "frequency": string | null,
      "duration": string | null
    }}
  ],
  "advice": [string],
  "follow_up": [string]
}}
""")
])


# ==============================
# Main Parsing Function
# ==============================

def parse_prescription(ocr_text: str) -> dict:
    """
    Converts raw OCR text into structured prescription JSON.
    """

    try:
        logger.info("[Parser] Sending OCR text to LLM for structuring.")

        formatted_prompt = prompt.invoke({
            "ocr_text": ocr_text
        })

        response = get_chat_groq(GPT_OSS_120B).invoke(formatted_prompt)

        parsed_json = json.loads(response.content.strip())

        validated = PrescriptionData(**parsed_json)

        logger.info("[Parser] Structured parsing successful.")

        return validated.model_dump()

    except Exception:
        logger.exception("[Parser] Parsing failed.")
        raise
