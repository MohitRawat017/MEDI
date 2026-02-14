"""
Test 1: GPU/CUDA Detection & HuggingFace Imports
Tests that PyTorch sees the GPU and that all HF models load correctly.
Run: python tests/test_gpu_and_imports.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"
WARN = "\033[93m⚠ WARN\033[0m"

def divider(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ── 1. PyTorch & CUDA ──────────────────────────────────────
divider("1. PyTorch & CUDA Detection")

try:
    import torch
    print(f"  PyTorch version      : {torch.__version__}")
    print(f"  CUDA available       : {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"  CUDA version         : {torch.version.cuda}")
        print(f"  GPU name             : {torch.cuda.get_device_name(0)}")
        print(f"  GPU memory (total)   : {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")
        print(f"  cuDNN enabled        : {torch.backends.cudnn.enabled}")
        print(f"  cuDNN version        : {torch.backends.cudnn.version()}")

        # Quick tensor test on GPU
        t = torch.tensor([1.0, 2.0, 3.0]).cuda()
        print(f"  GPU tensor test      : {PASS}  (tensor on {t.device})")
    else:
        print(f"  {FAIL}  CUDA is NOT available!")
        print(f"  Possible causes:")
        print(f"    - PyTorch was installed with CPU-only build")
        print(f"    - Run: pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126")
        print(f"    - Or cu121, cu124 depending on your CUDA toolkit version")
        print(f"    - Check CUDA toolkit: nvcc --version")

    # Check if torch was built with CUDA
    print(f"\n  torch.cuda build info:")
    print(f"    torch+cuda compiled : {torch.version.cuda is not None}")
    print(f"    torch.__file__      : {torch.__file__}")

except Exception as e:
    print(f"  {FAIL}  PyTorch import failed: {e}")


# ── 2. SentenceTransformers ─────────────────────────────────
divider("2. SentenceTransformer (Embedding Model)")

try:
    from sentence_transformers import SentenceTransformer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Loading on device    : {device}")

    model = SentenceTransformer(
        "sentence-transformers/all-mpnet-base-v2",
        device=device
    )

    # Check which device the model is actually on
    actual_device = str(next(model.parameters()).device)
    print(f"  Model actual device  : {actual_device}")

    if "cuda" in actual_device:
        print(f"  {PASS}  Embedding model is on GPU")
    else:
        print(f"  {WARN}  Embedding model is on CPU (expected GPU if CUDA available)")

    # Test encoding
    test_embedding = model.encode(["Hello world"], convert_to_numpy=True)
    print(f"  Embedding shape      : {test_embedding.shape}")
    print(f"  Embedding test       : {PASS}")

except Exception as e:
    print(f"  {FAIL}  SentenceTransformer failed: {e}")


# ── 3. CrossEncoder (Reranker) ──────────────────────────────
divider("3. CrossEncoder (Reranker Model)")

try:
    from sentence_transformers import CrossEncoder

    device = "cuda" if torch.cuda.is_available() else "cpu"
    reranker = CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device=device
    )

    # Test prediction
    scores = reranker.predict([
        ("What is diabetes?", "Diabetes is a chronic metabolic condition.")
    ])
    print(f"  Reranker score       : {scores[0]:.4f}")
    print(f"  Reranker test        : {PASS}")

except Exception as e:
    print(f"  {FAIL}  CrossEncoder failed: {e}")


# ── 4. HuggingFace Hub ──────────────────────────────────────
divider("4. HuggingFace Hub")

try:
    import huggingface_hub
    print(f"  huggingface_hub ver  : {huggingface_hub.__version__}")

    from dotenv import load_dotenv
    load_dotenv()
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        print(f"  HF_TOKEN             : {'*' * 6}...{hf_token[-4:]}")
        print(f"  {PASS}  HF_TOKEN is set")
    else:
        print(f"  {WARN}  HF_TOKEN not found in .env (may not be needed for public models)")

except Exception as e:
    print(f"  {FAIL}  HuggingFace Hub failed: {e}")


# ── Summary ─────────────────────────────────────────────────
divider("SUMMARY")
cuda_ok = torch.cuda.is_available()
print(f"  GPU Ready            : {'YES ✓' if cuda_ok else 'NO ✗ — Models will run on CPU'}")
print(f"  Models will use      : {'cuda' if cuda_ok else 'cpu'}")
print()
