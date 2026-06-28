import requests

messages = [
    {
        "role": "user",
        "content": "Hello World"
    }
]

print(requests.post("http://127.0.0.1:8000", json={"content": messages}).json())
