"""
Medical Assistant API: FastAPI backend for AI-powered medical chatbot
Uses RAG (Retrieval Augmented Generation) with Pinecone vector database

Endpoints:
    - POST /upload_pdfs/: Upload and process PDF documents
    - POST /ask/: Query the system with medical questions

Architecture:
    - FastAPI web framework
    - Pinecone for vector storage
    - LangChain for RAG pipeline
    - Groq for LLM inference
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handler import catch_exception_middleware
from routes.upload_pdf import router as upload_router
from routes.ask_question import router as ask_router
from routes.upload_prescription import router as upload_prescription_router
from routes.ask_prescription import router as ask_prescription_router

# Initialize FastAPI app
app = FastAPI(
    title="Medical Assistant API",
    description="API for AI Medical Assistant Chatbot"
)

# ============================================================
# CORS CONFIGURATION
# ============================================================
# Allow all origins for development
# In production, restrict to specific frontend domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"]  # Allow all headers
)


# ============================================================
# MIDDLEWARE
# ============================================================
# Global exception handler catches all unhandled errors
app.middleware("http")(catch_exception_middleware)

# ============================================================
# ROUTERS
# ============================================================
# Register API routes
app.include_router(upload_router)  # PDF upload endpoint
app.include_router(ask_router)  # Question answering endpoint
app.include_router(upload_prescription_router) # Prescription upload endpoint
app.include_router(ask_prescription_router) # Prescription question answering endpoint