"""
Upload PDF Route: Endpoint for uploading and processing PDF documents
Handles file upload -> parsing -> chunking -> embedding -> vector storage
"""

from fastapi import APIRouter, UploadFile, File
from typing import List
from modules.load_vectorstore import load_vectorstore_async
from fastapi.responses import JSONResponse
from logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...), namespace: str = "default"):
    """Upload and process PDF files into the vector database."""
    try:
        logger.info("Received uploaded files")
        result = await load_vectorstore_async(files, namespace)
        logger.info("Documents added to vectorstore")
        return {
            "message": "Files processed and vectorstore updated",
            "stats": result
        }
    except Exception:
        logger.exception("Error during PDF upload")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"}
        )