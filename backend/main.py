from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import requests
import json
import os

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

async def chat_with_ai(content: str) -> str:
    def make_request() -> str:
        response = requests.post(
            url="https://ai.hackclub.com/proxy/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            data=json.dumps({
                "model": "openai/gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            })
        )
        return response.json()["choices"][0]["message"]["content"]
    return await asyncio.to_thread(make_request)

app = FastAPI()

class Content(BaseModel):
    content: str

@app.post("/")
async def test(content: Content) -> dict:
    response = await chat_with_ai(content.content)
    return {"response": response}

