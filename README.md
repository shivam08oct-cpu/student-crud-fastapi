# Students Database CRUD Application (+ Optional Ollama AI Extension)

**Internship Project Assignment — Python Backend Development**  
*Issued by: EWB Edu Tech Pvt. Ltd. | Internship Program*

---

## 📌 Project Overview

This is a production-ready Python backend application built to manage student records using full **CRUD (Create, Read, Update, Delete)** operations. The backend is developed using **FastAPI** for high-performance asynchronous RESTful APIs and **SQLite** (via **SQLAlchemy ORM**) for persistent, relational data storage.

Additionally, this project implements the **Optional Bonus: Local AI with Ollama extension**. It enables users to ask natural-language questions (e.g., *"How many students are there?"*, *"List students born after 2005"*, *"Which courses are offered?"*) grounded strictly on database records without executing raw or unrestricted SQL.

---

## 🎯 Key Features & Requirements

### 1. Mandatory Core CRUD Requirements
- **Create**: Add new student profiles to SQLite with automatic or custom unique `student_id` and strict contact validation.
- **Read**: List students with pagination, search by name/email/ID, and filter by course or birth date range (`born_after`, `born_before`). Retrieve individual profiles by either string `student_id` (e.g. `STU-1001`) or database primary key ID.
- **Update**: Full update (`PUT`) or partial update (`PATCH`) of student attributes with duplicate email detection.
- **Delete**: Safely delete a student record with detailed JSON response confirmation.
- **Validation**: Enforces non-empty names, date of birth in the past, valid email format, and at least one contact method (email and/or phone).

### 2. Optional Bonus: Local AI with Ollama
- **Local Model**: Configured to work seamlessly with local models such as `llama3.2:1b` via Ollama's HTTP API (`http://localhost:11434/api/generate`).
- **Contextual Grounding**: Extracts structured summaries and records securely in backend Python code and injects them as prompt context.
- **Strict Security**: The AI model **never** generates or executes unrestricted SQL commands. Real personal data is protected, and answers are strictly grounded in database facts.
- **Intelligent Graceful Fallback**: If Ollama is not running locally, the endpoint returns an accurate, rule-grounded answer based on live database statistics with a helpful instruction to launch Ollama.

---

## 🧱 Database Schema & Student Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | Integer (Primary Key) | Auto | Unique autoincrementing database ID |
| `student_id` | String(50) | Yes (Auto if omitted) | Unique student code (e.g. `STU-1001`) |
| `name` | String(100) | **Yes** | Full student name |
| `date_of_birth` | Date (`YYYY-MM-DD`) | **Yes** | Date of birth (cannot be in the future) |
| `email` | String(120) | Optional* | Unique email address |
| `phone` | String(30) | Optional* | Contact phone number |
| `course` | String(100) | Optional | Enrolled program / course |
| `address` | String(255) | Optional | Residential address |
| `enrollment_date` | Date (`YYYY-MM-DD`) | Optional | Defaults to registration date |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `updated_at` | DateTime | Auto | Record last update timestamp |

*\*Note: As specified in assignment requirements, at least one contact method (`email` and/or `phone`) must be supplied.*

---

## 📁 Project Directory Structure

```text
student-crud-fastapi/
│
├── app/
│   ├── __init__.py           # Package marker & metadata
│   ├── config.py             # Environment & application settings
│   ├── database.py           # SQLite engine, SessionLocal & get_db dependency
│   ├── models.py             # SQLAlchemy Student database model
│   ├── schemas.py            # Pydantic schemas, validators & request/response models
│   ├── crud.py               # Data access layer & safe summary extractor
│   ├── ai_service.py         # Ollama client & grounded query processor
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py       # REST API endpoints for Student CRUD & filters
│   │   └── ai.py             # Natural language AI query endpoint
│   └── main.py               # FastAPI entry point, CORS, lifespan & documentation
│
├── tests/
│   ├── __init__.py
│   └── test_students_api.py  # Comprehensive automated pytest test suite (14 tests)
│
├── seed_data.py              # Realistic sample data seed script (8 diverse records)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore configuration
└── README.md                 # Project documentation & assignment report
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.12)
- **pip** (Python package installer)
- *(Optional)* **Ollama** installed with `llama3.2:1b` for local generative AI features.

### 2. Setup Virtual Environment & Dependencies

```bash
# Clone repository or navigate to project directory
cd student-crud-fastapi

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default parameters in `.env`:
```env
APP_NAME="Students Database CRUD Application"
DATABASE_URL="sqlite:///./students.db"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.2:1b"
```

### 4. Seed Sample Database Records
Populate realistic sample student records (students in Computer Science, Data Science, AI, born across 2003-2007):
```bash
python seed_data.py
```
*Output: `Successfully seeded 8 new student record(s). Total in database: 8`*

### 5. Run the FastAPI Application
Start the uvicorn development server:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Interactive ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🧪 Automated Testing

Run the automated test suite with `pytest`:
```bash
pytest tests -v
```
All 14 unit and integration tests run against an isolated in-memory SQLite database:
```
tests/test_students_api.py::test_root_endpoint PASSED
tests/test_students_api.py::test_health_check PASSED
tests/test_students_api.py::test_create_student_success PASSED
tests/test_students_api.py::test_create_student_auto_generate_id PASSED
tests/test_students_api.py::test_create_student_validation_missing_contact PASSED
tests/test_students_api.py::test_create_student_validation_future_dob PASSED
tests/test_students_api.py::test_create_student_duplicate_student_id PASSED
tests/test_students_api.py::test_create_student_duplicate_email PASSED
tests/test_students_api.py::test_get_and_filter_students PASSED
tests/test_students_api.py::test_get_student_by_id_and_student_id PASSED
tests/test_students_api.py::test_update_student_full_put PASSED
tests/test_students_api.py::test_update_student_partial_patch PASSED
tests/test_students_api.py::test_delete_student PASSED
tests/test_students_api.py::test_ai_query_endpoint PASSED
======================== 14 passed in 3.51s ========================
```

---

## 📡 API Endpoints Reference

All endpoints are accessible both directly (e.g. `/students`) and with the canonical version prefix `/api/v1/students`.

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/` | API status, metadata & endpoint directory | 200 OK |
| `GET` | `/health` | Application & SQLite health check | 200 OK |
| `POST` | `/students` | Create a new student | 201 Created |
| `GET` | `/students` | List students (with filters & pagination) | 200 OK |
| `GET` | `/students/{student_id}` | Retrieve individual student by code or ID | 200 OK |
| `PUT` | `/students/{student_id}` | Full update of existing student | 200 OK |
| `PATCH` | `/students/{student_id}` | Partial update of existing student | 200 OK |
| `DELETE` | `/students/{student_id}` | Delete a student profile | 200 OK |
| `POST` | `/ai/ask` | Ask natural-language questions via Ollama AI | 200 OK |

---

## 💡 Example Requests & Responses

### 1. Create a Student (`POST /students`)
**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU-1009",
    "name": "Samar Bose",
    "date_of_birth": "2006-03-25",
    "email": "samar.bose@example.com",
    "phone": "+91-9876543299",
    "course": "Computer Science",
    "address": "14 Salt Lake, Kolkata",
    "enrollment_date": "2024-08-01"
  }'
```
**Response (`201 Created`):**
```json
{
  "id": 9,
  "student_id": "STU-1009",
  "name": "Samar Bose",
  "date_of_birth": "2006-03-25",
  "email": "samar.bose@example.com",
  "phone": "+91-9876543299",
  "course": "Computer Science",
  "address": "14 Salt Lake, Kolkata",
  "enrollment_date": "2024-08-01",
  "created_at": "2026-11-01T20:25:00.123456",
  "updated_at": "2026-11-01T20:25:00.123456"
}
```

---

### 2. List & Filter Students (`GET /students`)
**Filter by Course:**
```bash
curl -X GET "http://127.0.0.1:8000/students?course=Computer"
```
**Filter Students Born After 2005:**
```bash
curl -X GET "http://127.0.0.1:8000/students?born_after=2005-12-31"
```
**Response (`200 OK`):**
```json
{
  "total": 4,
  "count": 4,
  "skip": 0,
  "limit": 20,
  "students": [
    {
      "id": 2,
      "student_id": "STU-1002",
      "name": "Diya Patel",
      "date_of_birth": "2006-11-22",
      "email": "diya.patel@example.com",
      "phone": "+91-9876543211",
      "course": "Data Science",
      "address": "15 Ashram Road, Ahmedabad, Gujarat",
      "enrollment_date": "2024-07-15",
      "created_at": "2026-11-01T20:21:42.518659",
      "updated_at": "2026-11-01T20:21:42.518659"
    }
  ]
}
```

---

### 3. Get Student Profile (`GET /students/{student_id}`)
Lookup works with either `student_id` string or database numeric ID:
```bash
curl -X GET "http://127.0.0.1:8000/students/STU-1001"
# or
curl -X GET "http://127.0.0.1:8000/students/1"
```

---

### 4. Partial Update (`PATCH /students/{student_id}`)
**Request:**
```bash
curl -X PATCH "http://127.0.0.1:8000/students/STU-1001" \
  -H "Content-Type: application/json" \
  -d '{
    "course": "Artificial Intelligence & Data Science"
  }'
```

---

### 5. Delete a Student (`DELETE /students/{student_id}`)
**Request:**
```bash
curl -X DELETE "http://127.0.0.1:8000/students/STU-1009"
```
**Response (`200 OK`):**
```json
{
  "message": "Student 'Samar Bose' (ID: STU-1009) successfully deleted.",
  "details": {
    "id": 9,
    "student_id": "STU-1009",
    "name": "Samar Bose"
  }
}
```

---

### 6. Natural Language AI Query (`POST /ai/ask`)

#### Example Question 1: "How many students are there?"
**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/ai/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many students are there?"}'
```
**Response (`200 OK`):**
```json
{
  "question": "How many students are there?",
  "answer": "There are currently 8 student(s) registered in the database.",
  "grounded_records_count": 8,
  "sample_records_used": [ ... ],
  "model_used": "llama3.2:1b",
  "source": "grounded_rule_fallback"
}
```

#### Example Question 2: "List students born after 2005."
**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/ai/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "List students born after 2005"}'
```
**Response (`200 OK`):**
```json
{
  "question": "List students born after 2005",
  "answer": "Found 4 student(s) born after 2005:\n- Diya Patel (ID: STU-1002, Course: Data Science, DOB: 2006-11-22)\n- Ananya Iyer (ID: STU-1004, Course: Computer Science, DOB: 2006-08-30)\n- Meera Nair (ID: STU-1006, Course: Information Technology, DOB: 2007-03-12)\n- Pooja Reddy (ID: STU-1008, Course: Artificial Intelligence, DOB: 2006-12-05)",
  "grounded_records_count": 8,
  "sample_records_used": [ ... ],
  "model_used": "llama3.2:1b",
  "source": "grounded_rule_fallback"
}
```

---

## 🤖 Ollama Local AI Setup Guide

To run local LLM generation with Ollama:
1. Download Ollama from [ollama.com](https://ollama.com) and install it.
2. Pull and start the recommended model:
   ```bash
   ollama run llama3.2:1b
   ```
3. Ollama will start listening at `http://localhost:11434`.
4. When you send requests to `POST /ai/ask`, the FastAPI backend automatically routes queries to your local Ollama instance and returns generated natural language text with `source: "ollama"`.

---

## ✅ Project Review Checklist

- [x] **Create Operation**: Adds new student profiles with validation.
- [x] **Read Operation**: Lists, paginates, searches, and filters by course, DOB, and ID.
- [x] **Update Operation**: Supports both full (`PUT`) and partial (`PATCH`) updates.
- [x] **Delete Operation**: Permanently removes student records.
- [x] **SQLite Persistence**: Stored reliably via SQLAlchemy ORM.
- [x] **Input Validation & Missing Record Handling**: Returns 400 for duplicate IDs/emails, 422 for invalid payloads, and 404 for missing records.
- [x] **Optional AI Extension**: Natural language questions answered safely without unrestricted SQL.
- [x] **Automated Tests**: 14 tests covering all CRUD cases, validations, and edge conditions.
- [x] **Documentation**: Complete reproducible README and interactive Swagger UI.

---
*Created for EWB Edu Tech Pvt. Ltd. Internship Project Assignment.*
