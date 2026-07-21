# Rashid Dental Clinic - AI Assistant

An intelligent, safety-conscious, website-embeddable AI chatbot for **Rashid Dental Clinic**. The assistant uses Retrieval-Augmented Generation (RAG) over verified Markdown files to answer patient queries, manage appointment requests, provide source citations, and handle safety/emergency scenarios gracefully.

---

## 🌟 Key Features

* **RAG-Powered Q&A:** Heading-based Markdown chunking with dense vector search (via FAISS and SentenceTransformers) for accurate retrieval.
* **Source Attribution:** Displays source documents and section references with every factual answer.
* **Appointment Management:** Collects user details, performs input validation, and logs requests to an SQLite database.
* **Medical Safety Guardrails:** Automatically blocks diagnosis requests and medication advice; recognizes emergency red flags without diagnosing.
* **Prompt-Injection Defense:** Sanitizes inputs and enforces strict system prompts against unauthorized instruction overrides.
* **Session Memory & Context:** Tracks user conversation state locally across chat turns.

---

## 🏗 System Architecture

```
             +----------------------------+
             |    Frontend Chat Widget    |
             |   (HTML / CSS / JS UI)     |
             +--------------+-------------+
                            |
               HTTP POST    | Requests
                            v
             +----------------------------+
             |       FastAPI Server       |
             |        (main.py)           |
             +--------------+-------------+
                            |
   +------------------------+------------------------+
   |                                                 |
   v                                                 v
+--------------+                                  +--------------+
| Guardrails   | --(Safe?)--------------------->  |  RAG Engine  |
| (Safety Check)|                                  | (FAISS + ST) |
+--------------+                                  +-------+------+
|                                                  |
| (Appointments)                                   | (Query Vector)
v                                                  v
+--------------+                                  +--------------+
|  SQLite DB   |                                  | Knowledge    |
| (clinic.db)  |                                  | Base (.md)   |
+--------------+                                  +--------------+
```

---

## 📋 Technical Requirements & Environment Setup

### Prerequisites
* **Python 3.10+** installed
* **pip** (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/rashid-dental-assistant.git
   cd rashid-dental-assistant
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables Configuration:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Fill in your parameters inside `.env`.

---

## 🚀 Running the Application Locally

1. **Rebuild / Initialize the RAG Vector Index:**
   ```bash
   python rebuild.py
   ```

2. **Start the FastAPI Backend:**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
   * *API Documentation (Swagger UI):* `http://127.0.0.1:8000/docs`

3. **Launch the Frontend Chatbot:**
   Open `frontend/index.html` directly in any web browser, or use VS Code **Live Server**.

---

## 🛡 Security & Medical Safety Measures

1. **Strict Key Management:** API credentials and environment options are stored strictly in `.env` and excluded from source control via `.gitignore`.
2. **Medical Diagnosis Blocking:** The system interceptor identifies requests asking for medical diagnoses or prescription advice, steering users to seek professional evaluation.
3. **Emergency Escalation:** Detects warning signs (e.g., severe bleeding, facial swelling, difficulty breathing) and displays emergency contact information immediately.
4. **Input Sanitization & Injection Defense:** Filters out system override attempts (e.g., `"Ignore previous instructions"`) and truncates excessive payload lengths.
5. **Data Protection:** Appointment submissions validate standard regex fields and store data locally in `clinic.db` without exposing sensitive records across sessions.

---

## 📁 Project Structure

```
rashid-dental-assistant/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── routes/
│   │   │   ├── chat.py          # /api/chat endpoint
│   │   │   └── appointments.py  # /api/appointments endpoint
│   │   ├── services/
│   │   │   ├── guardrails.py    # Safety & injection checks
│   │   │   ├── rag_engine.py    # FAISS + SentenceTransformers
│   │   │   └── appointment_service.py
│   │   └── models/
│   │       └── schemas.py       # Pydantic models
│   ├── knowledge_base/          # Markdown source files
│   │   ├── services.md
│   │   ├── dentists.md
│   │   ├── timings-and-location.md
│   │   ├── appointments.md
│   │   └── faq.md
│   └── storage/                 # FAISS index & metadata
│       ├── clinic_index.faiss
│       └── clinic_metadata.json
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── chat-widget.css
│   └── js/
│       └── chat-widget.js
├── rebuild.py                   # Vector index builder
├── requirements.txt
├── .env.example
├── .gitignore
└── clinic.db                    # SQLite database
```

---

## 🔧 Environment Variables

### `.env.example`

```env
# Application Configuration
APP_NAME="Rashid Dental Assistant"
APP_ENV=development
PORT=8000

# LLM API Settings (If utilizing remote inference)
GEMINI_API_KEY=your_gemini_api_key_here

# Vector Store & Embedding Settings
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
FAISS_INDEX_PATH=backend/storage/clinic_index.faiss
METADATA_PATH=backend/storage/clinic_metadata.json
KNOWLEDGE_BASE_DIR=backend/knowledge_base

# Database Settings
DATABASE_URL=sqlite:///./clinic.db
```

---

## 📚 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Main chat endpoint accepting `{ "message": "...", "session_id": "..." }` |
| POST | `/api/appointments` | Create a new appointment request |
| GET | `/api/appointments` | List all appointment requests |
| GET | `/docs` | Swagger UI (auto-generated) |
| GET | `/health` | Health check endpoint |

---

## 🧪 Development & Testing

Run the test suite:
```bash
pytest tests/ -v
```

---

## 📄 License

MIT License — see `LICENSE` for details.

---

*Built with FastAPI, SentenceTransformers, FAISS, and SQLite.*
*For Rashid Dental Clinic — AI-powered patient assistance.*
