"""Medical Assistant API: FastAPI backend for the AI-powered medical chatbot.

Endpoints:
    - POST /upload_pdfs/: Upload and process PDF documents
    - POST /ask/: Query the system with medical questions
    - POST /upload_prescription/: OCR + parse a prescription image
    - POST /ask_prescription/: Ask about an uploaded prescription
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handler import catch_exception_middleware
from routes.upload_pdf import router as upload_router
from routes.ask_question import router as ask_router
from routes.upload_prescription import router as upload_prescription_router
from routes.ask_prescription import router as ask_prescription_router
from modules.config import ALLOWED_ORIGINS

app = FastAPI(
    title="Medical Assistant API",
    description="API for AI Medical Assistant Chatbot"
)

# CORS: comma-separated origins via ALLOWED_ORIGINS ("*" allows all).
# Credentials are only meaningful for specific origins, so they are enabled
# whenever the wildcard is not in use.
allowed_origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials="*" not in allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.middleware("http")(catch_exception_middleware)

app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(upload_prescription_router)
app.include_router(ask_prescription_router)
