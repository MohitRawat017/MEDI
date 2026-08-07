import os
import asyncio
import torch
from pathlib import Path

from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from modules.config import (
    PINECONE_API_KEY,
    PINECONE_ENV,
    PINECONE_INDEX_NAME,
    UPLOAD_DIR,
)

# ============================================================
# GPU/CPU CONFIGURATION
# ============================================================
device = "cuda" if torch.cuda.is_available() else "cpu"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# The Pinecone index and embedding model are built on first use so
# importing this module never downloads weights or touches the network.

_pc = None
_index = None
_embedding_model = None


def _get_pinecone() -> Pinecone:
    global _pc
    if _pc is None:
        _pc = Pinecone(api_key=PINECONE_API_KEY)
    return _pc


def _get_index():
    global _index
    if _index is None:
        pc = _get_pinecone()
        spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)
        existing = [i["name"] for i in pc.list_indexes()]
        if PINECONE_INDEX_NAME not in existing:
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=768,  # Matches all-mpnet-base-v2 embedding dimension
                metric="cosine",
                spec=spec,
            )
        _index = pc.Index(PINECONE_INDEX_NAME)
    return _index


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(
            "sentence-transformers/all-mpnet-base-v2",
            device=device
        )
    return _embedding_model


async def process_single_file(file, namespace: str):
    """Process one uploaded PDF and store it in Pinecone. Returns chunk count."""
    save_path = Path(UPLOAD_DIR) / file.filename
    with open(save_path, "wb") as f:
        f.write(file.file.read())

    loader = PyPDFLoader(str(save_path))
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    ids = [f"{Path(save_path).stem}-{i}" for i in range(len(chunks))]

    # Encode in a thread pool so the async loop is never blocked
    embeddings = await asyncio.to_thread(
        _get_embedding_model().encode,
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Pinecone stores only vectors, so the text must live in metadata for retrieval
    for i, (id_, embedding, metadata) in enumerate(zip(ids, embeddings, metadatas)):
        metadata["text"] = texts[i]

    _get_index().upsert(
        vectors=zip(ids, embeddings, metadatas),
        namespace=namespace
    )

    return len(chunks)


async def load_vectorstore_async(uploaded_files, namespace):
    """Process multiple PDF files concurrently."""
    tasks = [
        process_single_file(file, namespace)
        for file in uploaded_files
    ]
    results = await asyncio.gather(*tasks)

    return {
        "Files_Processed": len(uploaded_files),
        "Total_Chunks_Created": sum(results)
    }
