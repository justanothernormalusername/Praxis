from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import requests
import json
import os

app = FastAPI()

load_dotenv()
provider = "HACKCLUBAI"  # Choose HACKCLUBAI or OPENROUTER
model = "anthropic/claude-sonnet-4.6"


if provider == "HACKCLUBAI":
    API_KEY = os.getenv("HACKCLUBAI_API_KEY")
    URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
elif provider == "OPENROUTER":
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    URL = "https://openrouter.ai/api/v1/chat/completions"
else:
    raise Exception("Provider not found, please select between HACKCLUBAI and OPENROUTER")

# Tool template for chatbot to end conversation and summarize
tools = [
    {
        "type": "function",
        "function": {
            "name": "output_result",
            "description": "Always call after the third message, provide a summary of the conversation so far",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Summary of the conversation so far"
                    }
                },
                "required": ["summary"]
            }
        }
    }
]

# Returns a tuple (status, content, summary)
async def chat_with_ai(content: list) -> tuple:
    def make_request() -> tuple:
        status = "running"
        summary = ""

        response = requests.post(
            url = URL,
            headers = {"Authorization": f"Bearer {API_KEY}"},
            json = {
                "model": model,
                "messages": content,
                "tools": tools
            }
        )

        # Error handling
        if "error" in response.json():
            status = "error"
            return (status, response.json()["error"]["message"], summary)

        # Handle tool calling
        if response.json()["choices"][0]["finish_reason"] == "tool_calls":
            status = "done"
            summary = json.loads(response.json()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])["summary"]

        return (status, response.json()["choices"][0]["message"]["content"], summary)
    return await asyncio.to_thread(make_request)


class Content(BaseModel):
    messages: list

@app.post("/")
async def test(content: Content) -> dict:
    output = await chat_with_ai(content.messages)
    return {"status": output[0], "response": output[1], "summary": output[2]}

response_format = {
    'id': 'gen-1782648906-K7oEDMaPpinEye24z43b', 
    'object': 'chat.completion', 
    'created': 1782648906, 
    'model': 'anthropic/claude-4.6-sonnet-20260217', 
    'provider': 'Anthropic', 
    'system_fingerprint': None, 
    'service_tier': 'default', 
    'choices': [{
        'index': 0, 
        'logprobs': None, 
        'finish_reason': 'tool_calls', 
        'native_finish_reason': 'tool_use', 
        'message': {
            'role': 'assistant', 
            'content': '[BOT] I apologize for the delay! Let me call the summary function right now!', 
            'refusal': None, 
            'reasoning': None, 
            'tool_calls': [{
                'type': 'function', 
                'index': 0, 
                'id': 'toolu_01AkSqB3TXEESYqwuLLJNfax', 
                'function': {
                    'name': 'output_result', 
                    'arguments': '{"summary": "The user greeted the bot and shared that their favourite color is purple. The bot responded by noting that purple is associated with creativity, wisdom, and royalty, and asked about their preferred shade. The user then asked for the bot\'s name, and the bot explained it is an AI assistant without a specific name. The user then requested a summary of the conversation."}'
                    }
                }]
            }
        }], 
    'usage': {
        'prompt_tokens': 823, 
        'completion_tokens': 146, 
        'total_tokens': 969, 
        'cost': 0.004659, 
        'is_byok': False, 
        'prompt_tokens_details': {
            'cached_tokens': 0, 
            'cache_write_tokens': 0, 
            'audio_tokens': 0, 
            'video_tokens': 0
        }, 
        'cost_details': {
            'upstream_inference_cost': 0.004659, 
            'upstream_inference_prompt_cost': 0.002469, 
            'upstream_inference_completions_cost': 0.00219
        }, 
        'completion_tokens_details': {
            'reasoning_tokens': 0, 
            'image_tokens': 0, 
            'audio_tokens': 0
        }
    }
}

