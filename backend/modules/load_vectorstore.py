"""
Load Vectorstore Module: Handles PDF ingestion into Pinecone
Process: Upload -> Parse -> Split -> Embed -> Store
"""

import os
import asyncio
import torch
from pathlib import Path
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# ============================================================
# GPU/CPU CONFIGURATION
# ============================================================
device = "cuda" if torch.cuda.is_available() else "cpu"

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "Medi"

UPLOAD_DIR = "./uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================================
# PINECONE INITIALIZATION
# ============================================================
# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(
    cloud="aws",
    region=PINECONE_ENV
)

# Check if index exists, create if not
existing_indexes = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=768,  # Matches all-mpnet-base-v2 embedding dimension
        metric="cosine",  # Cosine similarity for semantic search
        spec=spec
    )

index = pc.Index(PINECONE_INDEX_NAME)

# ============================================================
# EMBEDDING MODEL
# ============================================================
# Using SentenceTransformer directly for better performance
# Note: We're NOT using HuggingFaceEmbeddings wrapper for faster encoding
embedding_model = SentenceTransformer(
    "sentence-transformers/all-mpnet-base-v2",
    device=device
)


# ============================================================
# PDF PROCESSING PIPELINE
# ============================================================
async def process_single_file(file, namespace: str):
    """
    Process one uploaded PDF and store in Pinecone.

    Args:
        file: FastAPI UploadFile object
        namespace (str): Pinecone namespace for organization

    Returns:
        int: Number of chunks created from this PDF

    Pipeline:
        1. Save uploaded file to disk
        2. Load PDF using PyPDFLoader
        3. Split into chunks using RecursiveCharacterTextSplitter
        4. Generate embeddings using SentenceTransformer
        5. Upsert vectors to Pinecone with metadata
    """
    # ============================================================
    # STEP 1: SAVE FILE
    # ============================================================
    save_path = Path(UPLOAD_DIR) / file.filename
    with open(save_path, "wb") as f:
        f.write(file.file.read())

    # ============================================================
    # STEP 2: LOAD PDF
    # ============================================================
    # PyPDFLoader extracts text from PDF pages
    loader = PyPDFLoader(str(save_path))
    documents = loader.load()

    # ============================================================
    # STEP 3: SPLIT INTO CHUNKS
    # ============================================================
    # RecursiveCharacterTextSplitter splits on paragraphs, sentences, words
    # chunk_size=500: Each chunk ~500 characters
    # chunk_overlap=50: 50 characters overlap between chunks for context
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)

    # Extract text and metadata
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]

    # Generate unique IDs for each chunk
    ids = [f"{Path(save_path).stem}-{i}" for i in range(len(chunks))]

    # ============================================================
    # STEP 4: GENERATE EMBEDDINGS
    # ============================================================
    # Run embedding in thread pool to avoid blocking async loop
    # encode() converts text chunks to 768-dimensional vectors
    embeddings = await asyncio.to_thread(
        embedding_model.encode,
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # ============================================================
    # STEP 5: UPSERT TO PINECONE
    # ============================================================
    # Store vectors with IDs and metadata in Pinecone
    # Note: Must store text in metadata since Pinecone only stores vectors
    for i, (id_, embedding, metadata) in enumerate(zip(ids, embeddings, metadatas)):
        metadata["text"] = texts[i]  # Add text to metadata for retrieval

    index.upsert(
        vectors=zip(ids, embeddings, metadatas),
        namespace=namespace
    )

    return len(chunks)


# ============================================================
# BATCH PROCESSING
# ============================================================
async def load_vectorstore_async(uploaded_files, namespace):
    """
    Process multiple PDF files concurrently.

    Args:
        uploaded_files (List[UploadFile]): List of PDF files
        namespace (str): Pinecone namespace

    Returns:
        dict: Stats about files processed and chunks created

    Note: Uses asyncio.gather() for concurrent processing
    """
    tasks = [
        process_single_file(file, namespace)
        for file in uploaded_files
    ]
    results = await asyncio.gather(*tasks)

    return {
        "Files_Processed": len(uploaded_files),
        "Total_Chunks_Created": sum(results)
    }