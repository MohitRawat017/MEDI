import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from modules.medical_api import fetch_rxnorm_id, fetch_dailymed_summary

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="openai/gpt-oss-120b",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a medical assistant.

You must answer strictly based on:
1. The patient's prescription data.
2. Official drug label information from DailyMed.
3. Standard drug information via RxNorm.

Do NOT invent facts.
If data is missing, say so clearly.
"""),
    ("human",
     """Prescription Data:
{prescription_json}

Drug API Data:
{api_data}

User Question:
{question}

Provide a medically grounded answer.
""")
])


def generate_api_answer(prescription_json: dict, question: str):
    medications = prescription_json.get("medications", [])

    api_context = []

    for med in medications:
        name = med.get("name")

        rx_id = fetch_rxnorm_id(name)
        dailymed_info = fetch_dailymed_summary(name)

        api_context.append({
            "drug": name,
            "rxnorm_id": rx_id,
            "dailymed_info": dailymed_info
        })

    formatted_prompt = prompt.invoke({
        "prescription_json": prescription_json,
        "api_data": api_context,
        "question": question
    })

    response = llm.invoke(formatted_prompt)

    return response.content
