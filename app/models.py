from sqlalchemy import Column, Integer, String, Date, DateTime, func
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False, doc="Unique student identifier (e.g., STU-1001)")
    name = Column(String(100), nullable=False, index=True, doc="Full name of the student")
    date_of_birth = Column(Date, nullable=False, doc="Date of birth (YYYY-MM-DD)")
    email = Column(String(120), unique=True, index=True, nullable=True, doc="Email address")
    phone = Column(String(30), nullable=True, doc="Contact phone number")
    course = Column(String(100), index=True, nullable=True, doc="Enrolled academic course or degree")
    address = Column(String(255), nullable=True, doc="Residential address")
    enrollment_date = Column(Date, nullable=True, doc="Date when student enrolled")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Student(id={self.id}, student_id='{self.student_id}', name='{self.name}', course='{self.course}')>"
