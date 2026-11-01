import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app import models
from app.main import app

from sqlalchemy.pool import StaticPool

# Use an in-memory SQLite database with StaticPool so all sessions share the same memory DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "Students Database CRUD Application"
    assert "endpoints" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"

def test_create_student_success():
    payload = {
        "student_id": "STU-9901",
        "name": "Tanvi Rao",
        "date_of_birth": "2004-06-15",
        "email": "tanvi.rao@example.com",
        "phone": "+91-9123456789",
        "course": "Computer Science",
        "address": "12 Residency Road, Bengaluru",
        "enrollment_date": "2023-08-01"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU-9901"
    assert data["name"] == "Tanvi Rao"
    assert data["email"] == "tanvi.rao@example.com"
    assert "id" in data

def test_create_student_auto_generate_id():
    payload = {
        "name": "Kabir Mehta",
        "date_of_birth": "2005-03-10",
        "email": "kabir.m@example.com",
        "course": "Data Science"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"].startswith("STU-")
    assert data["name"] == "Kabir Mehta"

def test_create_student_validation_missing_contact():
    # Both email and phone missing should be rejected
    payload = {
        "name": "No Contact Student",
        "date_of_birth": "2004-01-01"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422

def test_create_student_validation_future_dob():
    future_date = (date.today() + timedelta(days=5)).isoformat()
    payload = {
        "name": "Time Traveler",
        "date_of_birth": future_date,
        "email": "timetraveler@example.com"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422

def test_create_student_duplicate_student_id():
    payload = {
        "student_id": "STU-DUPLICATE",
        "name": "First Entry",
        "date_of_birth": "2004-01-01",
        "email": "first@example.com"
    }
    res1 = client.post("/students", json=payload)
    assert res1.status_code == 201

    payload2 = {
        "student_id": "STU-DUPLICATE",
        "name": "Second Entry",
        "date_of_birth": "2004-01-01",
        "email": "second@example.com"
    }
    res2 = client.post("/students", json=payload2)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"]

def test_create_student_duplicate_email():
    payload1 = {
        "name": "Alice",
        "date_of_birth": "2004-01-01",
        "email": "shared@example.com"
    }
    res1 = client.post("/students", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "name": "Bob",
        "date_of_birth": "2004-01-01",
        "email": "shared@example.com"
    }
    res2 = client.post("/students", json=payload2)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"]

def test_get_and_filter_students():
    # Insert 3 students
    client.post("/students", json={
        "student_id": "STU-A",
        "name": "Alice Green",
        "date_of_birth": "2003-05-10",
        "email": "alice@test.com",
        "course": "Computer Science"
    })
    client.post("/students", json={
        "student_id": "STU-B",
        "name": "Bob Blue",
        "date_of_birth": "2006-08-20",  # Born 2006
        "email": "bob@test.com",
        "course": "Artificial Intelligence"
    })
    client.post("/students", json={
        "student_id": "STU-C",
        "name": "Charlie White",
        "date_of_birth": "2007-02-14",  # Born 2007
        "email": "charlie@test.com",
        "course": "Computer Science"
    })

    # 1. Total list
    res = client.get("/students")
    assert res.status_code == 200
    assert res.json()["total"] == 3

    # 2. Filter by course
    res = client.get("/students?course=Computer")
    assert res.status_code == 200
    assert res.json()["total"] == 2

    # 3. Filter by search keyword
    res = client.get("/students?search=Bob")
    assert res.status_code == 200
    assert res.json()["total"] == 1
    assert res.json()["students"][0]["student_id"] == "STU-B"

    # 4. Filter born after 2005-12-31
    res = client.get("/students?born_after=2005-12-31")
    assert res.status_code == 200
    assert res.json()["total"] == 2

def test_get_student_by_id_and_student_id():
    res_create = client.post("/students", json={
        "student_id": "STU-FINDME",
        "name": "Find Me",
        "date_of_birth": "2004-01-01",
        "email": "findme@example.com"
    })
    created = res_create.json()
    numeric_id = created["id"]

    # Retrieve by student_id string
    res_str = client.get("/students/STU-FINDME")
    assert res_str.status_code == 200
    assert res_str.json()["name"] == "Find Me"

    # Retrieve by numeric primary key
    res_num = client.get(f"/students/{numeric_id}")
    assert res_num.status_code == 200
    assert res_num.json()["student_id"] == "STU-FINDME"

    # Not found case
    res_404 = client.get("/students/NONEXISTENT")
    assert res_404.status_code == 404

def test_update_student_full_put():
    res_create = client.post("/students", json={
        "student_id": "STU-UPDATE",
        "name": "Old Name",
        "date_of_birth": "2004-01-01",
        "email": "old@example.com",
        "course": "Mechanical"
    })
    assert res_create.status_code == 201

    put_payload = {
        "name": "New Name",
        "date_of_birth": "2004-01-01",
        "email": "new@example.com",
        "course": "Computer Science"
    }
    res_put = client.put("/students/STU-UPDATE", json=put_payload)
    assert res_put.status_code == 200
    assert res_put.json()["name"] == "New Name"
    assert res_put.json()["course"] == "Computer Science"
    assert res_put.json()["email"] == "new@example.com"

def test_update_student_partial_patch():
    client.post("/students", json={
        "student_id": "STU-PATCH",
        "name": "Patch Name",
        "date_of_birth": "2004-01-01",
        "email": "patch@example.com",
        "course": "Civil"
    })

    patch_payload = {
        "course": "Artificial Intelligence"
    }
    res_patch = client.patch("/students/STU-PATCH", json=patch_payload)
    assert res_patch.status_code == 200
    assert res_patch.json()["course"] == "Artificial Intelligence"
    assert res_patch.json()["name"] == "Patch Name"  # preserved

def test_delete_student():
    client.post("/students", json={
        "student_id": "STU-DELETE",
        "name": "To Delete",
        "date_of_birth": "2004-01-01",
        "email": "delete@example.com"
    })

    res_del = client.delete("/students/STU-DELETE")
    assert res_del.status_code == 200
    assert "successfully deleted" in res_del.json()["message"]

    # Verify not found
    res_verify = client.get("/students/STU-DELETE")
    assert res_verify.status_code == 404

    # Deleting again returns 404
    res_del2 = client.delete("/students/STU-DELETE")
    assert res_del2.status_code == 404

def test_ai_query_endpoint():
    # Insert a few students
    client.post("/students", json={
        "student_id": "STU-AI-1",
        "name": "Zara Khan",
        "date_of_birth": "2006-04-10",
        "email": "zara@example.com",
        "course": "AI & Robotics"
    })
    client.post("/students", json={
        "student_id": "STU-AI-2",
        "name": "Dev Joshi",
        "date_of_birth": "2004-09-18",
        "email": "dev@example.com",
        "course": "Computer Science"
    })

    # Test count question
    response = client.post("/ai/ask", json={"question": "How many students are there?"})
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert data["grounded_records_count"] == 2
    assert "2" in data["answer"]

    # Test born after question
    response_born = client.post("/ai/ask", json={"question": "List students born after 2005"})
    assert response_born.status_code == 200
    assert "Zara Khan" in response_born.json()["answer"]
