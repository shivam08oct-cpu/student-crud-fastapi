from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas
from app.ai_service import query_ollama_ai
from app.config import settings

router = APIRouter(prefix="/ai", tags=["Local AI (Ollama Extension)"])

@router.post(
    "/ask",
    response_model=schemas.AIQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask natural language questions about students data",
    description=(
        "Answers natural-language questions about students using a local Ollama model (e.g. llama3.2:1b). "
        "Database records are fetched safely by backend Python code and injected as grounded context. "
        "Unrestricted SQL is never executed."
    ),
)
async def ask_students_ai(
    query_in: schemas.AIQueryRequest,
    db: Session = Depends(get_db)
):
    answer, source, records_count, sample_records = await query_ollama_ai(
        question=query_in.question,
        db=db,
        model=query_in.model
    )

    return schemas.AIQueryResponse(
        question=query_in.question,
        answer=answer,
        grounded_records_count=records_count,
        sample_records_used=sample_records,
        model_used=query_in.model or settings.OLLAMA_MODEL,
        source=source
    )
