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

        # ============================================================
        # STEP 1: RETRIEVE RELEVANT CHUNKS
        # ============================================================
        # Uses hybrid retrieval:
        # - Dense retrieval: Get top 7 chunks via vector similarity
        # - Reranking: Use cross-encoder to refine to top 4 most relevant
        documents = retrieve_with_rerank(
            query=user_input,
            namespace=namespace
        )

        if not documents:
            return {
                "response": "I'm sorry, but I couldn't find relevant information in the provided context",
                "source": []
            }

        # ============================================================
        # STEP 2: BUILD CONTEXT
        # ============================================================
        # Combine retrieved chunks into single context string
        # This context will be inserted into the LLM prompt
        context = "\n\n".join([doc["text"] for doc in documents])

        # ============================================================
        # STEP 3: GENERATE ANSWER
        # ============================================================
        # Send context + question to LLM for answer generation
        answer = generate_answer(
            question=user_input,
            context=context
        )

        # ============================================================
        # STEP 4: FORMAT RESPONSE
        # ============================================================
        # Extract source file paths from document metadata
        response = {
            "response": answer,
            "source": [
                doc["metadata"].get("source", "")
                for doc in documents
            ]
        }

        logger.debug("Query processed successfully")
        return response

    except Exception as e:
        logger.exception("Error in query chain")
        raise


# ============================================================
# ALTERNATIVE APPROACH: Using LangChain Chains
# ============================================================
# Instead of manual retrieval + generation, you can use LangChain's
# built-in chains that automate the RAG pipeline
#
# from langchain.chains import create_retrieval_chain
#
# def query_chain_with_langchain(user_input: str, chain):
#     """
#     Alternative implementation using LangChain's retrieval chain
#
#     Args:
#         user_input (str): User's question
#         chain: Pre-built LangChain retrieval chain (LCEL or RetrievalQA)
#
#     Returns:
#         dict: Response with answer and sources
#
#     How it works internally:
#         1. Chain receives query
#         2. Retriever fetches relevant documents from vector DB
#         3. Documents are combined and inserted into prompt template
#         4. LLM generates answer based on prompt
#         5. Returns result with source documents
#     """
#     try:
#         # For LCEL chains: use invoke()
#         result = chain.invoke({"query": user_input})
#
#         # For RetrievalQA: result format is {"result": answer, "source_documents": [...]}
#         response = {
#             "response": result["result"],
#             "sources": [
#                 doc.metadata.get("source", "")
#                 for doc in result["source_documents"]
#             ]
#         }
#
#         logger.debug(f"Chain response: {response}")
#         return response
#
#     except Exception as e:
#         logger.exception("Error in query chain")
#         raise
