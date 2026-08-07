# 🏥 AI Medical Assistant (Multimodal + Hybrid Intelligence)

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![LLM](https://img.shields.io/badge/LLM-Groq-purple)
![OCR](https://img.shields.io/badge/OCR-LightOnOCR-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed)
![CI](https://github.com/MohitRawat017/MEDI/actions/workflows/ci.yml/badge.svg)
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

## 🔬 OCR Benchmark Results

Benchmarked **LightOnOCR-2-1B** against **GLM-OCR** across 6 diverse prescription formats. LightOn achieved higher structured extraction F1 and medication recall on oncology prescriptions.

### Performance Comparison

| Engine | CER ↓ | WER ↓ | Layout Score ↑ | Structured F1 ↑ | Med Recall ↑ |
|--------|-------|-------|----------------|-----------------|---------------|
| **LightOnOCR-2-1B** | 1.886 | 1.876 | **0.789** | 0.833 | **0.500** |
| **GLM-OCR** | **0.929** | **1.127** | 0.616 | **0.946** | 0.417 |

*Lower is better for CER/WER, higher is better for other metrics*

### Per-Prescription Breakdown (Structured F1)

| Prescription Type | LightOnOCR | GLM-OCR | Notes |
|------------------|------------|---------|-------|
| **DOD** (Military) | 1.00 | 1.00 | Both perfect |
| **TALAT** (Certificate) | 1.00 | 1.00 | Both perfect |
| **ASHOK** (Pediatric) | 1.00 | 1.00 | Both perfect |
| **SANJEEV** (Complex) | 0.00 | 0.92 | GLM handles complexity better |
| **BAKER** (Historical) | 1.00 | 1.00 | Both perfect |
| **ORIGINAL** (Oncology) | **1.00** | 0.75 | **LightOn excels on cancer prescriptions** |

### Key Findings

- **GLM-OCR** achieves better character/word recognition (50% lower error rates)
- **LightOnOCR** preserves layout structure better (+28% layout score)
- **LightOnOCR** shows superior performance on oncology/cancer hospital prescriptions
- Both engines achieve perfect structured extraction on standard prescription formats
- GLM-OCR more robust on complex multi-medication prescriptions

*Full evaluation methodology: Character Error Rate (CER), Word Error Rate (WER), Layout Preservation, Medication Detection Recall, Structured JSON F1 via Groq gpt-oss-120b*

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
- 🌐 **Live Drug Knowledge** via RxNorm, DailyMed, RxClass, OpenFDA
- 🧠 **Deterministic Medical Answering** (temperature=0)
- ⚠️ **Drug Interaction Detection** (RxClass + LLM analysis)
- 📊 **Confidence Scoring** (diagnosis, normalization, overall)
- 🛡️ **Hallucination Detection** (post-answer grounding check)
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
│   │   ├── config.py                     # Central env config (keys, Pinecone, uploads)
│   │   ├── ocr.py                        # OCR extraction (lazy loading)
│   │   ├── prescription_parser.py        # LLM-based parsing
│   │   ├── medical_api.py                # RxNorm/DailyMed/RxClass/OpenFDA
│   │   ├── api_answer_chain.py           # Prescription Q&A chain
│   │   ├── confidence_scorer.py          # Confidence scoring
│   │   ├── drug_interaction_checker.py   # Drug interaction detection
│   │   ├── evaluation.py                 # F1/grounding/hallucination
│   │   ├── session_store.py              # In-memory session storage
│   │   ├── llm.py                        # Lazy ChatGroq factory
│   │   ├── retrieval.py                  # Pinecone retrieval + reranking
│   │   └── load_vectorstore.py           # PDF ingestion
│   ├── routes/
│   │   ├── upload_prescription.py        # POST /upload_prescription/
│   │   ├── ask_prescription.py           # POST /ask_prescription/
│   │   ├── upload_pdf.py                 # POST /upload_pdfs/
│   │   └── ask_question.py               # POST /ask/
│   ├── tests/
│   │   ├── test_logic.py                 # 🆕 Pure-logic tests (runs in CI, no keys)
│   │   ├── test_evaluation.py            # Evaluation metrics (live APIs)
│   │   ├── test_prescription_pipeline.py
│   │   ├── test_api_endpoints.py
│   │   └── run_all_tests.py
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PrescriptionUpload.jsx    # + confidence & interactions UI
│   │   │   ├── PrescriptionChat.jsx      # + hallucination banners
│   │   │   ├── FileUpload.jsx
│   │   │   └── ChatArea.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│   ├── Dockerfile
│   ├── nginx.conf                       # API reverse proxy + SPA fallback
│   └── package.json
│
├── docker-compose.yml                   # 🆕 One-command local stack
├── render.yaml                          # 🆕 Render blueprint (deploy)
└── .github/workflows/ci.yml             # 🆕 Lint + logic tests + optional live tests
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
  "prescription_data": {"patient_info": {}, "diagnosis": "", "medications": []},
  "interactions": {
    "interactions": [{"drug_pair": ["A","B"], "risk_level": "High", "description": "..."}],
    "disclaimer": "Advisory only"
  },
  "confidence": {
    "overall_confidence": "Medium",
    "diagnosis_confidence": "Medium",
    "api_grounding_coverage": 85.0,
    "medication_scores": []
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
| **RxClass** | Drug class lookup | ❌ No |
| **DailyMed** | FDA drug label data | ❌ No |
| **OpenFDA** | Adverse event signals | ❌ No |
| **Pinecone** | Vector DB for RAG | ✅ Yes |
| **Groq** | High-performance LLM inference | ✅ Yes |

---

## ⚙️ Tech Stack

**Backend:**
- Python 3.12+
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

### Option A — Docker Compose (recommended)

```bash
# 1. Configure secrets (one time)
cp backend/.env.example .env
# ... edit .env and paste your GROQ_API_KEY + PINECONE_API_KEY

# 2. Build and run the whole stack
docker compose up --build
```

Visit `http://localhost` (frontend) and `http://localhost:8000/docs` (API docs).
Models download from HuggingFace on first use (persisted in a volume).

### Option B — Local development

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# For GPU support, install torch first:
#   pip install torch --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt

cp .env.example .env   # then add your keys
uvicorn main:app --reload --port 8000
```

**Frontend** (the Vite dev server proxies API calls to `localhost:8000`):

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` (frontend) and `http://localhost:8000/docs` (API docs).

### 🔑 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ | — | Groq LLM key (backend) |
| `PINECONE_API_KEY` | ✅ | — | Pinecone vector DB key (backend) |
| `PINECONE_ENV` | ❌ | `us-east-1` | Pinecone region |
| `PINECONE_INDEX_NAME` | ❌ | `medi` | Pinecone index name |
| `ALLOWED_ORIGINS` | ❌ | `*` | Comma-separated CORS origins |
| `UPLOAD_DIR` | ❌ | `./uploaded_pdfs` | Where uploaded files are saved |
| `VITE_API_URL` | ❌ | same-origin | Frontend → backend base URL (frontend) |

---

## ☁️ Deployment (Render)

A [Render blueprint](render.yaml) is included: a Docker web service for the backend and a static site for the frontend.

1. Push this repo to GitHub and create a Render account.
2. In Render: **New → Blueprint** and point it at the repo (or run `render blueprint launch`).
3. Set the dashboard secrets (marked `sync: false` in the blueprint):
   - Backend: `GROQ_API_KEY`, `PINECONE_API_KEY`, and `ALLOWED_ORIGINS` = your frontend URL (e.g. `https://medi-frontend.onrender.com`)
   - Frontend: `VITE_API_URL` = `https://medi-backend.onrender.com`

> ⚠️ **Free tier limits — read this first.** Render's free web service allows **512MB RAM**, but the OCR engine (LightOnOCR-2-1B) needs ~4.2GB of weights alone. On the free tier:
> - ✅ General Q&A (RAG) works — mpnet + MiniLM reranker fit in ~260MB.
> - ❌ **Prescription OCR will crash with out-of-memory.**
> - To run OCR you need a paid instance (≥4GB RAM) or a GPU instance. Also expect the service to spin down after ~15 min idle and model weights to download on first use.
>
> For a quick demo on free hardware, use the RAG mode (upload PDFs → ask) or run the full stack locally with Docker Compose.

---

## 🤖 CI / CD

GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR:

- **Backend** — syntax check + `tests/test_logic.py` (pure logic, mocked APIs, no keys)
- **Frontend** — `npm ci` → lint → production build

A third **live-tests** job runs only when triggered manually (Actions → **Run workflow** → tick **run_live**) and exercises the real RxNorm/DailyMed grounding, Groq LLM, and Pinecone connection. It needs `GROQ_API_KEY` and `PINECONE_API_KEY` configured as repository secrets.

---

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

### Phase 3 ✅
- [x] Drug interaction detection (RxClass + LLM)
- [x] Confidence scoring (diagnosis + normalization + grounding)
- [x] Hallucination detection (post-answer grounding check)
- [x] OpenFDA adverse event integration
- [x] Evaluation framework (F1, grounding, hallucination metrics)

### Phase 4 🔮
- [x] Containerization (Docker + Compose)
- [x] Render deployment blueprint
- [x] CI/CD pipeline (lint, logic tests, optional live tests)
- [ ] Persistent storage (Redis / PostgreSQL)
- [ ] Multi-visit longitudinal tracking
- [ ] Contraindication alerts
- [ ] Medical intent router (auto-select mode)

---

## 🧪 Testing

```bash
cd backend/tests

# Pure-logic tests (no keys, CI-safe - also runs in GitHub Actions)
python test_logic.py

# Run all tests
python run_all_tests.py

# Run evaluation metrics (live RxNorm/DailyMed calls)
python test_evaluation.py
```

**Test Coverage:**
- GPU & HuggingFace imports
- Pinecone connection
- LLM (Groq) connection
- API endpoints (all 4)
- Prescription pipeline (end-to-end)
- Evaluation metrics (F1, grounding, confidence)

---

## 📊 Evaluation

| Metric | Description | Method |
|--------|-------------|--------|
| **Parsing F1** | Accuracy of JSON extraction vs ground truth | Leaf-value comparison |
| **API Grounding** | % of drugs resolved in RxNorm/DailyMed | Per-drug API check |
| **Diagnosis Confidence** | High (full text) / Medium (abbreviation) / Low (inferred) | Rule-based |
| **Hallucination Rate** | Unsupported claims in LLM answers | LLM fact-checking |
| **Overall Confidence** | min(all stage confidences) | Conservative floor |

Run `python tests/test_evaluation.py` to evaluate on sample prescriptions.

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