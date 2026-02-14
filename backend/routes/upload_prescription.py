import uuid
import os
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from modules.ocr import extract_text_from_image
from modules.prescription_parser import parse_prescription
from modules.session_store import save_session

router = APIRouter()

UPLOAD_DIR = "./uploaded_prescriptions"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload_prescription/")
async def upload_prescription(file: UploadFile = File(...)):
    try:
        # Save file
        filename = file.filename or "upload"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # OCR
        ocr_text = extract_text_from_image(file_path)

        # Parse to structured JSON
        structured_json = parse_prescription(ocr_text)

        # Create session ID
        session_id = str(uuid.uuid4())

        # Store session
        save_session(session_id, structured_json)

        return {
            "session_id": session_id,
            "prescription_data": structured_json
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
