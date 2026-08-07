"""
Retrieval Module: Handles document retrieval from Pinecone vector store
Implements hybrid retrieval: Dense retrieval + Cross-encoder reranking
"""

import torch
from typing import List, Dict

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, CrossEncoder
from logger import setup_logger
from modules.config import PINECONE_API_KEY, PINECONE_INDEX_NAME

logger = setup_logger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"[Retrieval] Using device: {device}")

# The Pinecone index and models are built on first use so importing
# this module never downloads weights or touches the network.

_pc = None
_index = None
_embedding_model = None
_reranker = None


def _get_index():
    global _pc, _index
    if _index is None:
        if _pc is None:
            _pc = Pinecone(api_key=PINECONE_API_KEY)
        _index = _pc.Index(PINECONE_INDEX_NAME)
    return _index


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(
            "sentence-transformers/all-mpnet-base-v2",
            device=device
        )
        _embedding_model.max_seq_length = 512
    return _embedding_model


def _get_reranker():
    global _reranker
    if _reranker is None:
        # Cross-encoders score query and document together, so they are more
        # accurate than the embedding model but slower - used as a second stage
        _reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            device=device
        )
    return _reranker


def dense_retrieval(query: str, top_k: int = 7, namespace: str = "default") -> List[Dict]:
    """Retrieve documents via vector similarity search."""
    query_embedding = _get_embedding_model().encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    results = _get_index().query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        namespace=namespace,
        include_metadata=True
    )

    return [
        {
            "text": match["metadata"]["text"],
            "score": match["score"],
            "metadata": match["metadata"]
        }
        for match in results["matches"]
    ]


def rerank(query: str, documents: List[Dict], top_n: int = 4) -> List[Dict]:
    """Rerank documents with a cross-encoder and keep the top-n."""
    if not documents:
        return []

    pairs = [(query, doc["text"]) for doc in documents]
    scores = _get_reranker().predict(pairs)

    for doc, score in zip(documents, scores):
        doc["rerank_score"] = float(score)

    return sorted(documents, key=lambda x: x["rerank_score"], reverse=True)[:top_n]


def retrieve_with_rerank(
    query: str,
    namespace: str,
    initial_k: int = 7,
    final_k: int = 4
) -> List[Dict]:
    """Two-stage retrieval: dense search followed by cross-encoder reranking."""
    initial_docs = dense_retrieval(
        query=query,
        namespace=namespace,
        top_k=initial_k
    )

    return rerank(
        query=query,
        documents=initial_docs,
        top_n=final_k
    )
