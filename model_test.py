from dotenv import load_dotenv
import requests
import os

load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"

message = "ABC"
model = "anthropic/claude-sonnet-4.6"
content = [{"role": "user", "content": message}]
tools = [{"name": "web search"}, {"name": "text developer"}]

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

# print(make_request().json())

with open("praxis_orchestrator_prompt.md") as f:
    content = f.read()
print(content)