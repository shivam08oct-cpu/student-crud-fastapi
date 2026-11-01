"""
Utility script to populate sample student data for demonstration and testing.
Run with: python seed_data.py
"""
import sys
import os
from datetime import date

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app import models

SAMPLE_STUDENTS = [
    {
        "student_id": "STU-1001",
        "name": "Aarav Sharma",
        "date_of_birth": date(2004, 5, 14),
        "email": "aarav.sharma@example.com",
        "phone": "+91-9876543210",
        "course": "Computer Science",
        "address": "42 MG Road, Bengaluru, Karnataka",
        "enrollment_date": date(2023, 8, 1),
    },
    {
        "student_id": "STU-1002",
        "name": "Diya Patel",
        "date_of_birth": date(2006, 11, 22),  # Born after 2005
        "email": "diya.patel@example.com",
        "phone": "+91-9876543211",
        "course": "Data Science",
        "address": "15 Ashram Road, Ahmedabad, Gujarat",
        "enrollment_date": date(2024, 7, 15),
    },
    {
        "student_id": "STU-1003",
        "name": "Rohan Verma",
        "date_of_birth": date(2003, 2, 19),
        "email": "rohan.verma@example.com",
        "phone": "+91-9876543212",
        "course": "Artificial Intelligence",
        "address": "88 Park Street, Kolkata, West Bengal",
        "enrollment_date": date(2022, 8, 10),
    },
    {
        "student_id": "STU-1004",
        "name": "Ananya Iyer",
        "date_of_birth": date(2006, 8, 30),  # Born after 2005
        "email": "ananya.iyer@example.com",
        "phone": "+91-9876543213",
        "course": "Computer Science",
        "address": "21 T Nagar, Chennai, Tamil Nadu",
        "enrollment_date": date(2024, 8, 5),
    },
    {
        "student_id": "STU-1005",
        "name": "Vikram Singh",
        "date_of_birth": date(2005, 1, 10),
        "email": "vikram.singh@example.com",
        "phone": "+91-9876543214",
        "course": "Cyber Security",
        "address": "77 Civil Lines, Jaipur, Rajasthan",
        "enrollment_date": date(2023, 7, 20),
    },
    {
        "student_id": "STU-1006",
        "name": "Meera Nair",
        "date_of_birth": date(2007, 3, 12),  # Born after 2005
        "email": "meera.nair@example.com",
        "phone": "+91-9876543215",
        "course": "Information Technology",
        "address": "10 Marine Drive, Kochi, Kerala",
        "enrollment_date": date(2024, 9, 1),
    },
    {
        "student_id": "STU-1007",
        "name": "Karan Malhotra",
        "date_of_birth": date(2004, 9, 25),
        "email": "karan.m@example.com",
        "phone": "+91-9876543216",
        "course": "Data Science",
        "address": "55 Connaught Place, New Delhi",
        "enrollment_date": date(2023, 8, 12),
    },
    {
        "student_id": "STU-1008",
        "name": "Pooja Reddy",
        "date_of_birth": date(2006, 12, 5),  # Born after 2005
        "email": "pooja.reddy@example.com",
        "phone": "+91-9876543217",
        "course": "Artificial Intelligence",
        "address": "33 Banjara Hills, Hyderabad, Telangana",
        "enrollment_date": date(2024, 8, 20),
    },
]

def seed_database():
    print("Initializing database tables...")
    init_db()
    db = SessionLocal()
    try:
        inserted_count = 0
        for data in SAMPLE_STUDENTS:
            existing = db.query(models.Student).filter(
                (models.Student.student_id == data["student_id"]) | 
                (models.Student.email == data["email"])
            ).first()

            if not existing:
                student = models.Student(**data)
                db.add(student)
                inserted_count += 1

        db.commit()
        total_now = db.query(models.Student).count()
        print(f"Successfully seeded {inserted_count} new student record(s). Total in database: {total_now}")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
