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
    """
    Upload and process PDF files into the vector database.

    Args:
        files (List[UploadFile]): List of PDF files to process
        namespace (str): Pinecone namespace for organization (default: "default")

    Returns:
        dict: Success message with processing statistics

    Response format:
        {
            "message": "Files processed and vectorstore updated",
            "stats": {
                "Files_Processed": 2,
                "Total_Chunks_Created": 150
            }
        }

    Error response:
        {
            "Error": "Error message"
        }

    Process:
        1. Receive PDF files
        2. Save files to disk
        3. Parse PDFs and extract text
        4. Split text into chunks
        5. Generate embeddings
        6. Store vectors in Pinecone
    """
    try:
        logger.info("Received uploaded files")
        result = await load_vectorstore_async(files, namespace)
        logger.info("Documents added to vectorstore")
        return {
            "message": "Files processed and vectorstore updated",
            "stats": result
        }
    except Exception as e:
        logger.exception("Error during PDF upload")
        return JSONResponse(
            status_code=500,
            content={"Error": str(e)}
        )