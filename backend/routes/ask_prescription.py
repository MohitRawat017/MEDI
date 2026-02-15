from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from modules.session_store import get_session
from modules.api_answer_chain import generate_api_answer
from modules.evaluation import detect_hallucinations

router = APIRouter()


@router.post("/ask_prescription/")
async def ask_prescription(
    session_id: str = Form(...),
    question: str = Form(...)
):
    try:
        session = get_session(session_id)

        if not session:
            return JSONResponse(
                status_code=404,
                content={"error": "Invalid session_id"}
            )

        prescription_json = session["prescription"]
        api_results = session.get("api_results", [])
        confidence = session.get("confidence", {})

        # Generate answer
        answer = generate_api_answer(prescription_json, question)

        # Hallucination detection runs AFTER answer generation
        # Does not modify answer, only flags risk
        hallucination_check = detect_hallucinations(
            answer, prescription_json, api_results
        )

        return {
            "answer": answer,
            "hallucination_check": hallucination_check,
            "confidence": confidence
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
