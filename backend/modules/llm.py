"""
LLM Module: Handles language model initialization and answer generation
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ============================================================
# LLM INITIALIZATION
# ============================================================
# Using Groq's hosted LLM for fast inference
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=GROQ_API_KEY,
    temperature=0  # Deterministic responses for medical queries
)

# ============================================================
# PROMPT TEMPLATE
# ============================================================
# ChatPromptTemplate provides structured conversation format
# System message: Defines the AI's role and behavior
# Human message: Contains the context (retrieved documents) + user question
custom_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a medical assistant. Use the following context to answer the question. If the context does not contain the answer, respond with 'I don't know'."),
    ("human", "{context}\n\nQuestion: {question}\n\nAnswer:")
])

# ============================================================
# CURRENT IMPLEMENTATION: Manual RAG Pipeline
# ============================================================
def generate_answer(question: str, context: str):
    """
    Generate an answer using the LLM with provided context.

    Args:
        question (str): User's question
        context (str): Retrieved document chunks combined into text

    Returns:
        str: Generated answer from the LLM

    Process:
        1. Format the prompt with context and question
        2. Invoke LLM with the formatted prompt
        3. Return the text response
    """
    formatted_prompt = custom_prompt.invoke({
        "context": context,
        "question": question
    })

    response = llm.invoke(formatted_prompt)
    return response.content


# ============================================================
# ALTERNATIVE APPROACH #1: LangChain LCEL Chains
# ============================================================
# This approach uses LangChain Expression Language (LCEL) to create
# a more automated RAG pipeline that handles retrieval + generation
#
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
#
# def get_llm_chain_with_lcel(retriever):
#     """
#     Creates an LCEL-based retrieval chain that automatically:
#     - Retrieves documents using the retriever
#     - Stuffs documents into the prompt context
#     - Generates answer with LLM
#     """
#     # Combine retrieved docs into context
#     document_chain = create_stuff_documents_chain(
#         llm=llm,
#         prompt=custom_prompt
#     )
#
#     # Create retrieval pipeline
#     retrieval_chain = create_retrieval_chain(
#         retriever=retriever,  # Fetches relevant documents from vector DB
#         combine_documents_chain=document_chain  # Combines docs + generates answer
#     )
#
#     return retrieval_chain
#
# Usage: result = retrieval_chain.invoke({"input": user_question})


# ============================================================
# ALTERNATIVE APPROACH #2: RetrievalQA (Legacy)
# ============================================================
# RetrievalQA is an older LangChain pattern that abstracts the RAG pipeline
# It's simpler but less flexible than LCEL chains
#
# from langchain.prompts import PromptTemplate
# from langchain.chains import RetrievalQA
#
# def get_llm_chain_with_retrievalqa(retriever):
#     """
#     Creates a RetrievalQA chain (older LangChain pattern)
#
#     How RetrievalQA works internally:
#     1. Embed User Query -> Converts question to vector embedding
#     2. Retrieve Relevant Chunks -> Calls retriever.get_relevant_documents(query)
#     3. Insert into Prompt -> Takes chunks and inserts into prompt template
#     4. Generate Answer -> LLM processes prompt and returns answer
#     """
#     # Legacy PromptTemplate format
#     custom_prompt = PromptTemplate(
#         input_variables=["context", "question"],
#         template="""
#         You are a medical assistant. Use the following context to answer the question.
#         If the context does not contain the answer, respond with "I don't know".
#
#         Context: {context}
#         Question: {question}
#
#         Answer:"""
#     )
#
#     return RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=retriever,
#         chain_type="map_reduce",  # Can be "stuff", "map_reduce", "refine", or "map_rerank"
#         chain_type_kwargs={"prompt": custom_prompt},
#         return_source_documents=True
#     )
#
# Usage: result = retrieval_qa.invoke({"query": user_question})