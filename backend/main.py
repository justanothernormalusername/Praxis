"""
Assignment: Student Grade Tracker API
Background
You are building a simple REST API for a university grade tracker. Students can be registered, have grades submitted for them, and retrieve their average grade. All data can be stored in a plain Python dictionary in memory — no database needed.

Requirements
Model a student record with the following fields:

name — a string
student_id — an integer
grades — a list of floats


Implement the following four routes:
1. POST /students

Register a new student. Accepts name and student_id. Their grades list starts empty. Returns a confirmation message.
2. GET /students/{student_id}

Return the student's name, id, and grades list. If the student doesn't exist, return a 404 error with a meaningful message.
3. POST /students/{student_id}/grades

Add a grade (a single float) to a student's grades list. If the student doesn't exist, return a 404.
4. GET /students/{student_id}/average

Return the student's average grade. If they have no grades yet, return a meaningful message instead of crashing.

Deliverables

A single main.py file
A sender.py that tests all four routes and prints the responses


Constraints

No external libraries beyond FastAPI, Pydantic, and requests
Don't look up how to do 404 errors specifically — reason through it yourself first, then look it up if needed
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

student_record = {}

class Student(BaseModel):
    name: str
    student_id: int
    grades: list[float] = []

@app.post("/student")
async def add_student(student: Student) -> dict:
    student_record[student.student_id] = {"name": student.name, "grades": student.grades}
    return {"response": f"{student.name} created with id: {student.student_id}"}

@app.get("/student/{student_id}")
async def get_student(student_id: int) -> dict:
    if student_record[student_id]:
        student = student_record[student_id]
        return {"name": student["name"], "grades": student["grades"]}
    raise HTTPException(status_code=404, detail="Student not found")

@app.post("/student/{student_id}/grades")
async def add_grade(student_id: int) -> dict:
    return {"message": "Hello World"}

@app.get("/student/{student_id}/average")
async def root() -> dict:
    return {"message": "Hello World"}
