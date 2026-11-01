from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/students", tags=["Students"])

@router.post(
    "",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student record",
    description="Adds a new student to the SQLite database. Enforces unique student ID and email.",
)
def create_student(
    student_in: schemas.StudentCreate,
    db: Session = Depends(get_db)
):
    # Check if custom student_id is already taken
    if student_in.student_id:
        existing_by_id = crud.get_student_by_student_id(db, student_in.student_id.strip())
        if existing_by_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student ID '{student_in.student_id}' is already registered."
            )

    # Check if email is already taken
    if student_in.email:
        existing_by_email = crud.get_student_by_email(db, student_in.email.lower())
        if existing_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{student_in.email}' is already registered."
            )

    return crud.create_student(db, student_in)


@router.get(
    "",
    response_model=schemas.PaginatedStudentResponse,
    status_code=status.HTTP_200_OK,
    summary="List and filter students",
    description="Retrieve student records with optional filtering by course, name/email search, date of birth range, and pagination.",
)
def list_students(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    course: Optional[str] = Query(None, description="Filter by course name (case-insensitive substring)"),
    search: Optional[str] = Query(None, description="Search term matching student name, ID, or email"),
    born_after: Optional[date] = Query(None, description="Filter students born after this date (YYYY-MM-DD)"),
    born_before: Optional[date] = Query(None, description="Filter students born before this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    students, total = crud.get_students(
        db,
        skip=skip,
        limit=limit,
        course=course,
        search=search,
        born_after=born_after,
        born_before=born_before,
    )
    return {
        "total": total,
        "count": len(students),
        "skip": skip,
        "limit": limit,
        "students": students,
    }


@router.get(
    "/{student_id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get student details",
    description="Retrieve a single student record by their student_id (e.g., 'STU-1001') or database numeric ID.",
)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_identifier(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found."
        )
    return student


@router.put(
    "/{student_id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Full update of student details",
    description="Replaces all editable fields of an existing student record.",
)
def update_student_full(
    student_id: str,
    student_in: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_identifier(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found."
        )

    # Check for email collision if email is updated
    if student_in.email and student_in.email.lower() != (student.email or "").lower():
        existing = crud.get_student_by_email(db, student_in.email.lower())
        if existing and existing.id != student.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{student_in.email}' is already in use by another student."
            )

    return crud.update_student(db, student, student_in, partial=False)


@router.patch(
    "/{student_id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Partial update of student details",
    description="Updates only the fields provided in the request body for the specified student.",
)
def update_student_partial(
    student_id: str,
    student_in: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_identifier(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found."
        )

    # Check for email collision if email is updated
    if student_in.email and student_in.email.lower() != (student.email or "").lower():
        existing = crud.get_student_by_email(db, student_in.email.lower())
        if existing and existing.id != student.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{student_in.email}' is already in use by another student."
            )

    return crud.update_student(db, student, student_in, partial=True)


@router.delete(
    "/{student_id}",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a student record",
    description="Removes the student from the database permanently.",
)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_identifier(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' was not found."
        )

    deleted_info = {
        "id": student.id,
        "student_id": student.student_id,
        "name": student.name
    }
    crud.delete_student(db, student)
    return {
        "message": f"Student '{student.name}' (ID: {student.student_id}) successfully deleted.",
        "details": deleted_info
    }
