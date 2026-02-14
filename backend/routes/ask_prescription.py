from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from modules.session_store import get_session
from modules.api_answer_chain import generate_api_answer

router = APIRouter()


@router.post("/ask_prescription/")
async def ask_prescription(
    session_id: str = Form(...),
    question: str = Form(...)
):
    try:
        prescription_json = get_session(session_id)

        if not prescription_json:
            return JSONResponse(
                status_code=404,
                content={"error": "Invalid session_id"}
            )

        answer = generate_api_answer(prescription_json, question)

        return {
            "answer": answer
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
