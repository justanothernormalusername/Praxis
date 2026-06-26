import requests

print(requests.post("http://127.0.0.1:8000/student", json={"name": "Harry", "student_id": 15}).json())

print(requests.get("http://127.0.0.1:8000/student").json())