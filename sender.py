import requests

print(requests.get("http://127.0.0.1:8000").json())

print(requests.post("http://127.0.0.1:8000/animal", json={"name": "Harry", "weight": 15}).json())
