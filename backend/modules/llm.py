"""
LLM Module: Handles language model initialization and answer generation
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from modules.config import GROQ_API_KEY

GPT_OSS_20B = "openai/gpt-oss-20b"
GPT_OSS_120B = "openai/gpt-oss-120b"

# Built lazily per model so importing this module never requires an API key
_llm_cache = {}


def get_chat_groq(model: str):
    if model not in _llm_cache:
        _llm_cache[model] = ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0  # Deterministic responses for medical queries
        )
    return _llm_cache[model]

custom_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a medical assistant. Use the following context to answer the question. If the context does not contain the answer, respond with 'I don't know'."),
    ("human", "{context}\n\nQuestion: {question}\n\nAnswer:")
])

def generate_answer(question: str, context: str):
    """Generate an answer from the given retrieved context."""
    formatted_prompt = custom_prompt.invoke({
        "context": context,
        "question": question
    })

    response = get_chat_groq(GPT_OSS_20B).invoke(formatted_prompt)
    return response.content

