from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import requests
import json
import os

app = FastAPI()

load_dotenv()
PROVIDER = "HACKCLUBAI"  # Choose HACKCLUBAI or OPENROUTER
MODEL = "~anthropic/claude-sonnet-latest"


if PROVIDER == "HACKCLUBAI":
    API_KEY = os.getenv("HACKCLUBAI_API_KEY")
    URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
elif PROVIDER == "OPENROUTER":
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    URL = "https://openrouter.ai/api/v1/chat/completions"
else:
    raise Exception("Provider not found, please select between HACKCLUBAI and OPENROUTER")


async def chat_with_ai(content: list) -> str:
    def make_request() -> str:
        response = requests.post(
            url = URL,
            headers = {"Authorization": f"Bearer {API_KEY}"},
            data = json.dumps({
                "model": MODEL,
                "messages": content
            })
        )
        # Error handling
        if "error" in response.json():
            return response.json()["error"]["message"]
        return response.json()["choices"][0]["message"]["content"]
    
    return await asyncio.to_thread(make_request)


class Content(BaseModel):
    content: list

@app.post("/")
async def test(content: Content) -> dict:
    response = await chat_with_ai(content.content)
    return {"response": response}

