FROM python:3.12-slim

# Build as non-root; Render free tier and Compose both run this image.
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# Install CPU-only torch first so the CUDA runtime (~2.5GB) never ships.
# The bare `torch` in requirements.txt is then already satisfied.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Keep model weights and uploads in writable, persistent locations.
ENV HF_HOME=/app/.cache/huggingface \
    UPLOAD_DIR=/app/uploaded_pdfs \
    PYTHONUNBUFFERED=1

RUN mkdir -p /app/uploaded_pdfs /app/.cache/huggingface && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
