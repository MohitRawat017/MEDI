# 🏥 AI Medical Assistant (Multimodal + Hybrid Intelligence)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![LLM](https://img.shields.io/badge/LLM-Groq-purple)
![OCR](https://img.shields.io/badge/OCR-LightOnOCR-orange)
![Status](https://img.shields.io/badge/Status-Active-success)

> OCR-powered prescription understanding + Live Drug Knowledge APIs  
> Built with FastAPI, LightOnOCR, Groq LLM, RxNorm, and DailyMed

---

## 🚀 Overview

AI Medical Assistant is a dual-mode intelligent system that can:

1. 📄 **Understand handwritten prescriptions** using OCR
2. 🧠 **Convert prescriptions into structured medical JSON**
3. 💊 **Explain medications** using live medical APIs (RxNorm + DailyMed)
4. 📚 **Answer general medical questions** via RAG (knowledge base mode)

This is not just a chatbot.  
It is a **multimodal medical reasoning system.**

---

## 🧠 System Architecture

### 🔹 Prescription Intelligence Mode

```
┌─────────────────────┐
│  Prescription Image │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   LightOnOCR (GPU)  │
│ Layout-Aware OCR    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Groq LLM           │
│  Parsing + Cleanup  │
│  Normalization      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Structured JSON     │
│ (Validated Schema)  │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────┐
│ RxNorm + DailyMed APIs       │
│ (Live Drug Knowledge)        │
└──────────┬───────────────────┘
           ▼
    🧠 Grounded LLM Answer
```

---

### 🔹 General Medical Q&A Mode (RAG)

```
User Question
     │
     ▼
Vector Embeddings (SentenceTransformers)
     │
     ▼
Pinecone Retrieval + Reranking
     │
     ▼
Retrieved Context
     │
     ▼
LLM Grounded Answer
```

---

## ✨ Key Features

- 🔍 **Handwritten Prescription OCR** (LightOnOCR 2.1B)
- 🧾 **Structured Prescription Parsing** (Pydantic Schema Validation)
- 💊 **Drug Normalization & Standardization**
- 🌐 **Live Drug Knowledge** via:
  - RxNorm API
  - DailyMed API
- 🧠 **Deterministic Medical Answering**
- 📚 **Optional Static Knowledge Base** (RAG with Pinecone)
- ⚡ **FastAPI Backend**
- 🧩 **Session-based Prescription Storage**
- 🎨 **Modern React Frontend** with Tailwind CSS

---

## 📦 Project Structure

```
Medical_Chatbot/
├── backend/
│   ├── modules/
│   │   ├── ocr.py                    # OCR extraction
│   │   ├── prescription_parser.py    # LLM-based parsing
│   │   ├── medical_api.py            # RxNorm/DailyMed integration
│   │   ├── api_answer_chain.py       # Prescription Q&A chain
│   │   ├── session_store.py          # In-memory session storage
│   │   ├── llm.py                    # RAG LLM
│   │   ├── retrieval.py              # Pinecone retrieval + reranking
│   │   └── load_vectorstore.py       # PDF ingestion
│   │
│   ├── routes/
│   │   ├── upload_prescription.py    # POST /upload_prescription/
│   │   ├── ask_prescription.py       # POST /ask_prescription/
│   │   ├── upload_pdf.py             # POST /upload_pdfs/
│   │   └── ask_question.py           # POST /ask/
│   │
│   ├── tests/
│   │   ├── test_prescription_pipeline.py
│   │   ├── test_api_endpoints.py
│   │   └── run_all_tests.py
│   │
│   ├── main.py
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── PrescriptionUpload.jsx
    │   │   ├── PrescriptionChat.jsx
    │   │   ├── FileUpload.jsx
    │   │   └── ChatArea.jsx
    │   ├── services/
    │   │   └── api.js
    │   └── App.jsx
    └── package.json
```

---

## 🔌 API Endpoints

### 📤 Upload Prescription

```http
POST /upload_prescription/
Content-Type: multipart/form-data

file: <prescription_image>
```

**Returns:**

```json
{
  "session_id": "uuid-...",
  "prescription_data": {
    "patient_info": {...},
    "diagnosis": "...",
    "medications": [...]
  }
}
```

### ❓ Ask About Prescription

```http
POST /ask_prescription/
Content-Type: multipart/form-data

session_id: <uuid>
question: "What is the dosage for Denosumab?"
```

### 📚 Upload Knowledge Base PDFs

```http
POST /upload_pdfs/
Content-Type: multipart/form-data

files: <pdf_files>
namespace: "medical_kb"
```

### � Ask General Medical Question (RAG)

```http
POST /ask/
Content-Type: multipart/form-data

question: "What are the side effects of chemotherapy?"
namespace: "medical_kb"
```

---

## 🧠 Example Prescription JSON

```json
{
  "patient_info": {
    "name": "Dalia Kundu",
    "age": 64,
    "sex": "F",
    "appointment_date": "2024-01-15"
  },
  "diagnosis": "MBC (Metastatic Breast Cancer)",
  "medications": [
    {
      "name": "Denosumab (Xgeva)",
      "dose": "120 mg",
      "frequency": "Once monthly",
      "duration": "6 months"
    }
  ],
  "follow_up": [
    "Review after 3 months",
    "Monitor calcium levels"
  ]
}
```

---

## 🌐 External APIs Used

| API | Purpose | Auth Required |
|-----|---------|---------------|
| **RxNorm** | Drug normalization | ❌ No |
| **DailyMed** | FDA drug label data | ❌ No |
| **Pinecone** | Vector DB for RAG | ✅ Yes |
| **Groq** | High-performance LLM inference | ✅ Yes |

---

## ⚙️ Tech Stack

**Backend:**
- Python 3.10+
- FastAPI
- LightOnOCR 2.1B
- Groq LLM (via LangChain)
- SentenceTransformers (all-mpnet-base-v2)
- Cross-Encoder Reranker
- Pinecone
- Pydantic (schema validation)

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- Axios
- Lucide React (icons)
- React Markdown

---

## 🚀 Quick Start

### 1️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_key" >> .env
echo "PINECONE_API_KEY=your_pinecone_key" >> .env
echo "HF_TOKEN=your_huggingface_token" >> .env

# Run server
uvicorn main:app --reload --port 8000
```

### 2️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Visit `http://localhost:5173` (frontend) and `http://localhost:8000/docs` (API docs).

---

## 🧠 Design Philosophy

- ✅ **Deterministic medical responses** (temperature=0)
- ✅ **Schema validation** for safety (Pydantic models)
- ✅ **Clear separation** of RAG and Prescription modes
- ✅ **API-first hybrid architecture** (live APIs + static KB)
- ✅ **Modular backend engines** (easy to swap components)

---

## 🛣️ Roadmap

### Phase 1 ✅
- [x] OCR + Structured Parsing
- [x] Session-based prescription storage

### Phase 2 ✅
- [x] Live API Drug Grounding (RxNorm + DailyMed)
- [x] React frontend with tab navigation

### Phase 3 🚧
- [ ] Drug interaction detection
- [ ] Contraindication alerts
- [ ] Persistent storage (Redis / PostgreSQL)

### Phase 4 🔮
- [ ] Multi-visit longitudinal tracking
- [ ] Confidence scoring for OCR output
- [ ] OpenFDA adverse event integration
- [ ] Medical intent router (auto-select mode)

---

## 🧪 Testing

```bash
cd backend/tests

# Run all tests
python run_all_tests.py

# Run specific test
python test_prescription_pipeline.py
```

**Test Coverage:**
- GPU & HuggingFace imports
- Pinecone connection
- LLM (Groq) connection
- API endpoints (all 4)
- Prescription pipeline (end-to-end)

---

## ⚠️ Disclaimer

**This system is for educational and research purposes only.**  
It does not replace professional medical advice, diagnosis, or treatment.  
Always consult a qualified healthcare provider.

---

## 🎯 Use Cases

- 📋 **Digital prescription archiving**
- 💊 **Medication education** (patient-friendly explanations)
- 🔍 **Drug interaction checking** (roadmap)
- 📊 **Medical knowledge Q&A** (research assistant)

---

## 👨‍💻 Author

Built as an exploration of:
- Multimodal AI (OCR + LLM)
- Medical RAG systems
- Hybrid knowledge grounding (APIs + Vector DB)
- Real-world LLM orchestration
- Production-grade medical AI systems

---

## � License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **LightOnOCR** for layout-aware OCR
- **Groq** for blazing-fast LLM inference
- **RxNorm & DailyMed** for open medical APIs
- **Pinecone** for vector search infrastructure