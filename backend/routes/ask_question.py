"""
Ask Question Route: Endpoint for querying the RAG system
Accepts questions and returns AI-generated answers with sources
"""

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from modules.query_handlers import query_chain
from logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/ask/")
async def ask_question(question: str = Form(...), namespace: str = Form(...)):
    """
    Process a user question through the RAG pipeline.

    Args:
        question (str): User's medical question
        namespace (str): Pinecone namespace to query

    Returns:
        dict: Response containing answer and source documents

    Response format:
        {
            "response": "AI-generated answer",
            "source": ["source_file_1.pdf", "source_file_2.pdf"]
        }

    Error response:
        {
            "error": "Internal Server Error"
        }
    """
    try:
        logger.info(f"User query: {question}")

        result = query_chain(
            user_input=question,
            namespace=namespace
        )

        logger.info("Query successful")
        return result

    except Exception as e:
        logger.exception("Error processing question")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"}
        )
