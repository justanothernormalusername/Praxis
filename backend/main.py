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
            "description": "This tool is to be called when the end learning goal is fully clarified, and both you and the user have the a full exact picture of what they want to learn and accomplish from this experience.",
            "parameters": {
                "type": "object",
                "properties": {
                    "learning_details": {
                        "type": "string",
                        "description": "Provide a full detailed description of all the information about the user, including programming ability, topic expected to cover (in detail), specific learning requirements, notes based off the user's personality/behavior or other additional information that may help with problem set engagement."
                    }
                },
                "required": ["learning_details"]
            }
        }
    }
]

# Returns a tuple (status, content, learning_details)
async def chat_with_ai(content: list) -> tuple:
    def make_request() -> tuple:
        status = "running"
        learning_details = ""

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
            return (status, response.json()["error"]["message"], learning_details)

        # Handle tool calling
        if response.json()["choices"][0]["finish_reason"] == "tool_calls":
            status = "done"
            learning_details = json.loads(response.json()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])["learning_details"]

        return (status, response.json()["choices"][0]["message"]["content"], learning_details)
    return await asyncio.to_thread(make_request)


class Content(BaseModel):
    messages: list

@app.post("/")
async def test(content: Content) -> dict:
    output = await chat_with_ai(content.messages)
    return {"status": output[0], "response": output[1], "learning_details": output[2]}

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
            'content': '[BOT] I apologize for the delay! Let me call the learning_details function right now!', 
            'refusal': None, 
            'reasoning': None, 
            'tool_calls': [{
                'type': 'function', 
                'index': 0, 
                'id': 'toolu_01AkSqB3TXEESYqwuLLJNfax', 
                'function': {
                    'name': 'output_result', 
                    'arguments': '{"learning_details": "The user greeted the bot and shared that their favourite color is purple. The bot responded by noting that purple is associated with creativity, wisdom, and royalty, and asked about their preferred shade. The user then asked for the bot\'s name, and the bot explained it is an AI assistant without a specific name. The user then requested a learning_details of the conversation."}'
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

