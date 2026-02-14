"""
Test 2: Pinecone Connection & Index
Tests that Pinecone connects, the index exists, and has data.
Run: python tests/test_pinecone.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"
WARN = "\033[93m⚠ WARN\033[0m"

def divider(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ── 1. Pinecone Connection ──────────────────────────────────
divider("1. Pinecone Connection")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "medi"

if not PINECONE_API_KEY:
    print(f"  {FAIL}  PINECONE_API_KEY not found in .env")
    sys.exit(1)

print(f"  API Key              : {'*' * 6}...{PINECONE_API_KEY[-4:]}")

try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    print(f"  Connection           : {PASS}")
except Exception as e:
    print(f"  {FAIL}  Pinecone connection failed: {e}")
    sys.exit(1)


# ── 2. List Indexes ─────────────────────────────────────────
divider("2. Pinecone Indexes")

try:
    indexes = pc.list_indexes()
    index_names = [i["name"] for i in indexes]
    print(f"  Available indexes    : {index_names}")

    if INDEX_NAME in index_names:
        print(f"  Index '{INDEX_NAME}'       : {PASS}  Found")
    else:
        print(f"  {FAIL}  Index '{INDEX_NAME}' NOT found!")
        print(f"  Available: {index_names}")
        sys.exit(1)

except Exception as e:
    print(f"  {FAIL}  Failed to list indexes: {e}")
    sys.exit(1)


# ── 3. Index Stats ──────────────────────────────────────────
divider("3. Index Statistics")

try:
    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()

    total_vectors = stats.get("total_vector_count", 0)
    namespaces = stats.get("namespaces", {})

    print(f"  Total vectors        : {total_vectors}")
    print(f"  Dimension            : {stats.get('dimension', 'N/A')}")
    print(f"  Namespaces           : {list(namespaces.keys()) if namespaces else 'None'}")

    if namespaces:
        for ns, ns_stats in namespaces.items():
            count = ns_stats.get("vector_count", 0)
            print(f"    '{ns}' : {count} vectors")
    
    if total_vectors > 0:
        print(f"  Data present         : {PASS}")
    else:
        print(f"  {WARN}  Index is EMPTY — upload PDFs first")

except Exception as e:
    print(f"  {FAIL}  Failed to get index stats: {e}")


# ── 4. Test Query ────────────────────────────────────────────
divider("4. Test Vector Query")

try:
    import torch
    from sentence_transformers import SentenceTransformer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", device=device)

    test_query = "What is diabetes?"
    query_embedding = model.encode(test_query, convert_to_numpy=True, normalize_embeddings=True)

    # Try querying each namespace
    for ns in list(namespaces.keys()) if namespaces else ["default"]:
        results = index.query(
            vector=query_embedding.tolist(),
            top_k=3,
            namespace=ns,
            include_metadata=True
        )

        matches = results.get("matches", [])
        print(f"\n  Namespace '{ns}':")
        print(f"    Matches found      : {len(matches)}")

        if matches:
            for i, match in enumerate(matches[:3]):
                score = match.get("score", 0)
                text = match.get("metadata", {}).get("text", "N/A")[:80]
                print(f"    [{i+1}] score={score:.4f}  text=\"{text}...\"")
            print(f"    Query test         : {PASS}")
        else:
            print(f"    {WARN}  No matches found for test query")

except Exception as e:
    print(f"  {FAIL}  Query test failed: {e}")

print()
