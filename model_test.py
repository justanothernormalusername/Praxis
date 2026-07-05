from dotenv import load_dotenv
import requests
import os

load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"

message = input()
model = "anthropic/claude-sonnet-4.6"
content = [{"role": "user", "content": message}]
tools = []

def make_request() -> requests.models.Response:
    return requests.post(
        url = URL,
        headers = {"Authorization": f"Bearer {API_KEY}"},
        json = {
            "model": model,
            "messages": content,
            "tools": tools
        }
    )

print(make_request().json())