"""
Query Handler Module: Orchestrates the RAG pipeline
Retrieval -> Context Building -> LLM Generation
"""

from logger import setup_logger
from modules.retrieval import retrieve_with_rerank
from modules.llm import generate_answer

logger = setup_logger(__name__)


def query_chain(user_input: str, namespace: str):
    """
    Execute the complete RAG pipeline for a user question.

    Args:
        user_input (str): The user's question
        namespace (str): Pinecone namespace to query

    Returns:
        dict: Contains 'response' (answer) and 'source' (list of source files)

    Pipeline:
        1. Retrieve relevant document chunks using dense retrieval + reranking
        2. Combine chunks into context string
        3. Generate answer using LLM with context
        4. Return answer with source metadata
    """
    try:
        logger.debug(f"Running chain for input: {user_input}")

        documents = retrieve_with_rerank(
            query=user_input,
            namespace=namespace
        )

        if not documents:
            return {
                "response": "I'm sorry, but I couldn't find relevant information in the provided context",
                "source": []
            }

        context = "\n\n".join([doc["text"] for doc in documents])

        answer = generate_answer(
            question=user_input,
            context=context
        )

        response = {
            "response": answer,
            "source": [
                doc["metadata"].get("source", "")
                for doc in documents
            ]
        }

        logger.debug("Query processed successfully")
        return response

    except Exception:
        logger.exception("Error in query chain")
        raise
