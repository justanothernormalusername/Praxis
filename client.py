import requests

print(requests.post("http://127.0.0.1:8000", json={"content": "Hello World"}).json())