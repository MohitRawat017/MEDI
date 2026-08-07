"""Centralized configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "medi"
UPLOAD_DIR = "./uploaded_pdfs"
