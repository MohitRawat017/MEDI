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

app = FastAPI(
    title="Medical Assistant API",
    description="API for AI Medical Assistant Chatbot"
)

# Allow all origins for development; restrict to frontend domains in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.middleware("http")(catch_exception_middleware)

app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(upload_prescription_router)
app.include_router(ask_prescription_router)
