"""
Test 3: LLM (Groq) Connection & Generation
Tests that the Groq LLM is reachable and generates responses.
Run: python tests/test_llm.py
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


# ── 1. Groq API Key ─────────────────────────────────────────
divider("1. Groq API Key")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print(f"  {FAIL}  GROQ_API_KEY not found in .env")
    sys.exit(1)

print(f"  API Key              : {'*' * 6}...{GROQ_API_KEY[-4:]}")
print(f"  {PASS}  GROQ_API_KEY is set")


# ── 2. LangChain Groq Import ────────────────────────────────
divider("2. LangChain Groq Import")

try:
    from langchain_groq import ChatGroq
    print(f"  langchain_groq       : {PASS}  Imported")
except ImportError as e:
    print(f"  {FAIL}  langchain_groq import failed: {e}")
    print(f"  Fix: pip install langchain-groq")
    sys.exit(1)


# ── 3. LLM Initialization ───────────────────────────────────
divider("3. LLM Initialization")

try:
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=GROQ_API_KEY,
        temperature=0
    )
    print(f"  Model                : openai/gpt-oss-20b")
    print(f"  {PASS}  LLM initialized")
except Exception as e:
    print(f"  {FAIL}  LLM init failed: {e}")
    sys.exit(1)


# ── 4. Test Generation ──────────────────────────────────────
divider("4. Test LLM Generation")

try:
    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a medical assistant. Use the following context to answer the question. If the context does not contain the answer, respond with 'I don't know'."),
        ("human", "{context}\n\nQuestion: {question}\n\nAnswer:")
    ])

    test_context = "Diabetes mellitus is a group of metabolic diseases characterized by high blood sugar levels over a prolonged period. Symptoms include frequent urination, increased thirst, and increased hunger."
    test_question = "What are the symptoms of diabetes?"

    formatted = prompt.invoke({
        "context": test_context,
        "question": test_question
    })

    print(f"  Sending test query...")
    response = llm.invoke(formatted)

    print(f"  Response             : {response.content[:150]}...")
    print(f"  Token usage          : {response.response_metadata.get('token_usage', 'N/A')}")
    print(f"  {PASS}  LLM generation works")

except Exception as e:
    print(f"  {FAIL}  LLM generation failed: {e}")
    print(f"\n  If you see 'model not found', try changing the model in modules/llm.py")
    print(f"  Available Groq models: llama-3.3-70b-versatile, gemma2-9b-it, mixtral-8x7b-32768")


# ── 5. Test generate_answer function from llm.py ────────────
divider("5. Test generate_answer() from modules/llm.py")

try:
    from modules.llm import generate_answer

    answer = generate_answer(
        question="What is diabetes?",
        context="Diabetes is a chronic condition affecting blood sugar regulation."
    )
    print(f"  Answer               : {answer[:150]}...")
    print(f"  {PASS}  generate_answer() works")

except Exception as e:
    print(f"  {FAIL}  generate_answer() failed: {e}")

print()
