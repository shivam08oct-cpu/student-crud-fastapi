from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict

class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the student", examples=["Aarav Sharma"])
    date_of_birth: date = Field(..., description="Date of birth (YYYY-MM-DD)", examples=["2004-05-15"])
    email: Optional[EmailStr] = Field(None, description="Valid email address", examples=["aarav.sharma@example.com"])
    phone: Optional[str] = Field(None, max_length=30, description="Contact phone number", examples=["+91-9876543210"])
    course: Optional[str] = Field(None, max_length=100, description="Enrolled program/course", examples=["Computer Science"])
    address: Optional[str] = Field(None, max_length=255, description="Residential address", examples=["42 MG Road, Bengaluru, Karnataka"])
    enrollment_date: Optional[date] = Field(default_factory=date.today, description="Enrollment date (defaults to today)", examples=["2024-08-01"])

    @model_validator(mode="after")
    def validate_contact_and_dates(self):
        # 1. At least email or phone must be provided
        if not self.email and not self.phone:
            raise ValueError("At least one contact method (email or phone) must be provided.")
        
        # 2. DOB cannot be in the future
        if self.date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
            
        # 3. Clean strings
        if self.name.strip() == "":
            raise ValueError("Student name cannot be empty or blank.")
            
        return self

class StudentCreate(StudentBase):
    student_id: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Optional unique identifier (e.g., 'STU-1001'). If omitted, will be auto-generated.", 
        examples=["STU-1001"]
    )

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Aarav Sharma"])
    date_of_birth: Optional[date] = Field(None, examples=["2004-05-15"])
    email: Optional[EmailStr] = Field(None, examples=["aarav.new@example.com"])
    phone: Optional[str] = Field(None, max_length=30, examples=["+91-9876543211"])
    course: Optional[str] = Field(None, max_length=100, examples=["Data Science"])
    address: Optional[str] = Field(None, max_length=255, examples=["12 Indiranagar, Bengaluru"])
    enrollment_date: Optional[date] = Field(None, examples=["2024-08-01"])

    @model_validator(mode="after")
    def validate_update(self):
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        if self.name is not None and self.name.strip() == "":
            raise ValueError("Student name cannot be empty.")
        return self

class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: str
    name: str
    date_of_birth: date
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

class PaginatedStudentResponse(BaseModel):
    total: int
    count: int
    skip: int
    limit: int
    students: List[StudentResponse]

class MessageResponse(BaseModel):
    message: str
    details: Optional[dict] = None

# Ollama AI Extension Schemas
class AIQueryRequest(BaseModel):
    question: str = Field(
        ..., 
        min_length=3, 
        description="Natural language question about student records", 
        examples=["How many students are there?", "List students born after 2005", "Which courses are students enrolled in?"]
    )
    model: Optional[str] = Field(None, description="Optional Ollama model override (default: llama3.2:1b)")

class AIQueryResponse(BaseModel):
    question: str
    answer: str
    grounded_records_count: int
    sample_records_used: List[dict]
    model_used: str
    source: str = Field(description="'ollama' if answered via Ollama, or 'grounded_rule_fallback' if Ollama service is unavailable")
