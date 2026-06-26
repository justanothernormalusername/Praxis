import requests

# Create a Student
print(requests.post("http://127.0.0.1:8000/student", json={"name": "Harry", "student_id": 15}).json())

# Retrieve Student data
print(requests.get("http://127.0.0.1:8000/student/15").json())

# Returns a 404 Exception: Student not found
print(requests.get("http://127.0.0.1:8000/student/16").json())

# Returns a detail: Student has no grades
print(requests.get("http://127.0.0.1:8000/student/15/average").json())

# Adds a grade to the Student
print(requests.post("http://127.0.0.1:8000/student/15/grades", json={"grade": 97.0}).json())

# Adds a grade to the Student
print(requests.post("http://127.0.0.1:8000/student/15/grades", json={"grade": 98.0}).json())

# Return's Student's average grade
print(requests.get("http://127.0.0.1:8000/student/15/average").json())
