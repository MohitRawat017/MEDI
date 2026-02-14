"""
Retrieval Module: Handles document retrieval from Pinecone vector store
Implements hybrid retrieval: Dense retrieval + Cross-encoder reranking
"""

import os
import torch
from typing import List, Dict
from dotenv import load_dotenv

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, CrossEncoder

# Load environment variables
load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "medi"

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# ============================================================
# EMBEDDING MODEL
# ============================================================
# Sentence transformer for converting text to embeddings
# all-mpnet-base-v2: 768-dimensional embeddings, good for semantic similarity
embedding_model = SentenceTransformer(
    "sentence-transformers/all-mpnet-base-v2",
    device=device
)
embedding_model.max_seq_length = 512  # Truncate long sequences

# ============================================================
# RERANKER (CROSS-ENCODER)
# ============================================================
# Cross-encoder provides more accurate relevance scoring
# than bi-encoder (embedding model) but is slower
# Used as second-stage to refine initial retrieval results
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
    device=device
)

# ============================================================
# PINECONE INITIALIZATION
# ============================================================
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


# ============================================================
# STEP 1: DENSE RETRIEVAL
# ============================================================
def dense_retrieval(query: str, top_k: int = 7, namespace: str = "default") -> List[Dict]:
    """
    Retrieve documents using vector similarity search.

    Args:
        query (str): User's question
        top_k (int): Number of documents to retrieve
        namespace (str): Pinecone namespace to search in

    Returns:
        List[Dict]: Retrieved documents with text, score, and metadata

    Process:
        1. Embed the query into a 768-dimensional vector
        2. Query Pinecone for top_k most similar vectors
        3. Return documents with similarity scores
    """
    # Embed query
    query_embedding = embedding_model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Query Pinecone
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        namespace=namespace,
        include_metadata=True
    )

    # Extract documents
    documents = []
    for match in results['matches']:
        documents.append({
            "text": match["metadata"]["text"],
            "score": match["score"],
            "metadata": match["metadata"]
        })

    return documents


# ============================================================
# STEP 2: RERANKING
# ============================================================
def rerank(query: str, documents: List[Dict], top_n: int = 4) -> List[Dict]:
    """
    Rerank documents using cross-encoder for better relevance.

    Args:
        query (str): User's question
        documents (List[Dict]): Initially retrieved documents
        top_n (int): Number of documents to keep after reranking

    Returns:
        List[Dict]: Top-n reranked documents

    Why reranking?
        - Bi-encoders (embedding models) encode query and document separately
        - Cross-encoders process query + document together for better accuracy
        - Trade-off: More accurate but slower (suitable for reranking small set)
    """
    if not documents:
        return []

    # Create query-document pairs
    pairs = [(query, doc["text"]) for doc in documents]

    # Get relevance scores from cross-encoder
    scores = reranker.predict(pairs)

    # Add rerank scores to documents
    for doc, score in zip(documents, scores):
        doc["rerank_score"] = float(score)

    # Sort by rerank score and return top_n
    documents = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
    return documents[:top_n]


# ============================================================
# COMBINED RETRIEVAL PIPELINE
# ============================================================
def retrieve_with_rerank(
    query: str,
    namespace: str,
    initial_k: int = 7,
    final_k: int = 4
) -> List[Dict]:
    """
    Two-stage retrieval: Dense retrieval followed by reranking.

    Args:
        query (str): User's question
        namespace (str): Pinecone namespace
        initial_k (int): Number of docs to retrieve initially
        final_k (int): Number of docs to return after reranking

    Returns:
        List[Dict]: Top-k most relevant documents

    Pipeline:
        1. Dense Retrieval: Fast vector search to get ~7 candidates
        2. Reranking: Precise cross-encoder scoring to get top 4
    """
    # Step 1: Dense Retrieval
    initial_docs = dense_retrieval(
        query=query,
        namespace=namespace,
        top_k=initial_k
    )

    # Step 2: Rerank
    final_docs = rerank(
        query=query,
        documents=initial_docs,
        top_n=final_k
    )

    return final_docs 