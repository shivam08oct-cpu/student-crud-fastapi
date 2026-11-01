import uuid
from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app import models, schemas

def generate_unique_student_id(db: Session, prefix: str = "STU") -> str:
    """Generate a unique human-readable student_id like STU-1001 or STU-XXXX."""
    count = db.query(models.Student).count()
    candidate = f"{prefix}-{1001 + count}"
    # Verify uniqueness in case of deletions
    while db.query(models.Student).filter(models.Student.student_id == candidate).first():
        candidate = f"{prefix}-{uuid.uuid4().hex[:6].upper()}"
    return candidate

def get_student_by_id(db: Session, id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == id).first()

def get_student_by_student_id(db: Session, student_id: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()

def get_student_by_identifier(db: Session, identifier: str) -> Optional[models.Student]:
    """Find a student by either their student_id string (e.g. 'STU-1001') or numeric database primary key ID."""
    if identifier.isdigit():
        student = get_student_by_id(db, int(identifier))
        if student:
            return student
    return get_student_by_student_id(db, identifier)

def get_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.email == email).first()

def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    course: Optional[str] = None,
    search: Optional[str] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None,
) -> Tuple[List[models.Student], int]:
    query = db.query(models.Student)

    if course:
        query = query.filter(models.Student.course.ilike(f"%{course.strip()}%"))

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Student.name.ilike(search_term),
                models.Student.student_id.ilike(search_term),
                models.Student.email.ilike(search_term),
            )
        )

    if born_after:
        query = query.filter(models.Student.date_of_birth > born_after)

    if born_before:
        query = query.filter(models.Student.date_of_birth < born_before)

    total = query.count()
    students = query.order_by(models.Student.id.asc()).offset(skip).limit(limit).all()
    return students, total

def create_student(db: Session, student_in: schemas.StudentCreate) -> models.Student:
    student_id = student_in.student_id
    if not student_id or not student_id.strip():
        student_id = generate_unique_student_id(db)
    else:
        student_id = student_id.strip()

    db_student = models.Student(
        student_id=student_id,
        name=student_in.name.strip(),
        date_of_birth=student_in.date_of_birth,
        email=student_in.email.lower() if student_in.email else None,
        phone=student_in.phone.strip() if student_in.phone else None,
        course=student_in.course.strip() if student_in.course else None,
        address=student_in.address.strip() if student_in.address else None,
        enrollment_date=student_in.enrollment_date or date.today(),
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(
    db: Session,
    db_student: models.Student,
    student_in: schemas.StudentUpdate,
    partial: bool = False
) -> models.Student:
    update_data = student_in.model_dump(exclude_unset=partial)

    for field, value in update_data.items():
        if field == "email" and value:
            value = value.lower()
        elif isinstance(value, str):
            value = value.strip()
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, db_student: models.Student) -> None:
    db.delete(db_student)
    db.commit()

def get_safe_students_context(db: Session, max_records: int = 100) -> dict:
    """
    Safely retrieve student summaries to ground the AI model.
    Omits sensitive personal contact information (email, phone, address) to respect privacy,
    while providing structured stats and student records for accurate Q&A.
    """
    total_count = db.query(models.Student).count()
    
    # Course breakdown
    course_counts = (
        db.query(models.Student.course, func.count(models.Student.id))
        .group_by(models.Student.course)
        .all()
    )
    course_stats = {course or "Unassigned": count for course, count in course_counts}

    # Fetch safe record summaries
    students = db.query(models.Student).order_by(models.Student.id.asc()).limit(max_records).all()
    records = []
    for s in students:
        records.append({
            "student_id": s.student_id,
            "name": s.name,
            "birth_date": s.date_of_birth.isoformat() if s.date_of_birth else None,
            "birth_year": s.date_of_birth.year if s.date_of_birth else None,
            "course": s.course or "None",
            "enrollment_date": s.enrollment_date.isoformat() if s.enrollment_date else None,
        })

    return {
        "total_students": total_count,
        "courses_summary": course_stats,
        "students": records
    }
