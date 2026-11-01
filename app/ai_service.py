import re
import json
import logging
import httpx
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import get_safe_students_context

logger = logging.getLogger(__name__)

def build_grounded_prompt(question: str, context: dict) -> str:
    """Constructs a strictly grounded prompt with safe database context."""
    return f"""You are a helpful database assistant for an academic institution.
You have access to the following verified database records of students extracted from SQLite:

--- DATABASE CONTEXT START ---
Total registered students: {context['total_students']}
Courses breakdown: {json.dumps(context['courses_summary'], indent=2)}
Student records list:
{json.dumps(context['students'], indent=2)}
--- DATABASE CONTEXT END ---

User Question: {question}

Instructions:
1. Answer the question accurately using ONLY the verified database context provided above.
2. If asked about counts, lists, or filters (e.g., students born after a certain year, students in a specific course), list the matching students by their student_id, name, and relevant attribute.
3. If the information requested is not present in the records, state that clearly.
4. Do not make up or assume any student data that is not in the context.
5. Provide a direct, concise, and helpful human-readable answer.
"""

def generate_grounded_fallback_answer(question: str, context: dict) -> str:
    """
    Intelligent rule-based fallback when Ollama is offline or not installed.
    Guarantees that standard assignment demo questions get accurate, grounded answers.
    """
    q = question.lower()
    total = context.get("total_students", 0)
    students = context.get("students", [])

    # 1. Total count query
    if any(k in q for k in ["how many students", "total students", "count of students", "number of students"]):
        return f"There are currently {total} student(s) registered in the database."

    # 2. Born after / before year query (e.g., "List students born after 2005")
    match_after = re.search(r"born\s+after\s+(\d{4})", q)
    if match_after:
        year = int(match_after.group(1))
        matching = [s for s in students if s.get("birth_year") and s["birth_year"] > year]
        if not matching:
            return f"No students found born after {year}."
        lines = [f"- {s['name']} (ID: {s['student_id']}, Course: {s['course']}, DOB: {s['birth_date']})" for s in matching]
        return f"Found {len(matching)} student(s) born after {year}:\n" + "\n".join(lines)

    match_before = re.search(r"born\s+before\s+(\d{4})", q)
    if match_before:
        year = int(match_before.group(1))
        matching = [s for s in students if s.get("birth_year") and s["birth_year"] < year]
        if not matching:
            return f"No students found born before {year}."
        lines = [f"- {s['name']} (ID: {s['student_id']}, Course: {s['course']}, DOB: {s['birth_date']})" for s in matching]
        return f"Found {len(matching)} student(s) born before {year}:\n" + "\n".join(lines)

    # 3. Courses query
    if any(k in q for k in ["what courses", "which courses", "list courses", "available courses"]):
        courses = context.get("courses_summary", {})
        if not courses:
            return "No courses currently recorded."
        lines = [f"- {course}: {cnt} student(s)" for course, cnt in courses.items()]
        return "Courses and student enrollments:\n" + "\n".join(lines)

    # 4. Filter by course name query (e.g., "Who is studying Computer Science?")
    for course_name, cnt in context.get("courses_summary", {}).items():
        if course_name.lower() in q:
            matching = [s for s in students if s.get("course", "").lower() == course_name.lower()]
            lines = [f"- {s['name']} (ID: {s['student_id']})" for s in matching]
            return f"{cnt} student(s) are in {course_name}:\n" + "\n".join(lines)

    # 5. Generic summary fallback
    summary_list = [f"- {s['name']} (ID: {s['student_id']}, Course: {s['course']})" for s in students[:5]]
    more = f" ...and {total - 5} more." if total > 5 else ""
    return (
        f"Database contains {total} student(s). Sample records:\n"
        + "\n".join(summary_list)
        + more
        + "\n\n(Tip: Start Ollama with 'ollama run llama3.2:1b' for open-ended natural language generation!)"
    )

async def query_ollama_ai(
    question: str,
    db: Session,
    model: str = None
) -> Tuple[str, str, int, list]:
    """
    Executes a grounded query against Ollama or falls back gracefully.
    Returns: (answer, source, grounded_records_count, sample_records)
    """
    chosen_model = model or settings.OLLAMA_MODEL
    context = get_safe_students_context(db)
    records_count = context.get("total_students", 0)
    sample_records = context.get("students", [])[:10]

    prompt = build_grounded_prompt(question, context)

    # Attempt to query local Ollama instance
    ollama_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    try:
        # Fast connect timeout (0.5s) to avoid hanging when local Ollama is offline
        req_timeout = httpx.Timeout(settings.OLLAMA_TIMEOUT_SECONDS, connect=0.5)
        async with httpx.AsyncClient(timeout=req_timeout) as client:
            response = await client.post(
                ollama_url,
                json={
                    "model": chosen_model,
                    "prompt": prompt,
                    "stream": False,
                }
            )

            if response.status_code == 200:
                data = response.json()
                raw_response = data.get("response", "").strip()
                if raw_response:
                    return raw_response, "ollama", records_count, sample_records

            logger.warning("Ollama returned status %s: %s", response.status_code, response.text)

    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as err:
        logger.info("Local Ollama server not reachable at %s (%s). Using grounded fallback.", ollama_url, str(err))
    except Exception as err:
        logger.error("Unexpected error contacting Ollama: %s", str(err))

    # Return intelligent grounded fallback
    fallback_ans = generate_grounded_fallback_answer(question, context)
    return fallback_ans, "grounded_rule_fallback", records_count, sample_records
