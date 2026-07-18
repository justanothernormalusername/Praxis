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

chat_model = "tencent/hy3:free"
plan_model = "anthropic/claude-sonnet-5"

if provider == "HACKCLUBAI":
    API_KEY = os.getenv("HACKCLUBAI_API_KEY")
    URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
elif provider == "OPENROUTER":
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    URL = "https://openrouter.ai/api/v1/chat/completions"
else:
    raise Exception("Provider not found, please select between HACKCLUBAI and OPENROUTER")

# Returns a Request object
async def chat_with_ai(model: str, content: list, tools: list | None = None, response_format: dict | None = None) -> requests.models.Response:
    if tools is None:
        tools = []
    if response_format is None:
        response_format = {}
    def make_request() -> requests.models.Response:
        return requests.post(
            url = URL,
            headers = {"Authorization": f"Bearer {API_KEY}"},
            json = {
                "model": model,
                "messages": content,
                "tools": tools,
                "response_format": response_format
            }
        )
    response = await asyncio.to_thread(make_request)
    return response


class Content(BaseModel):
    messages: list

@app.post("/chat")
async def chatbot_handler(content: Content) -> dict:
    # Tool for chatbot to end conversation and output learning_details
    conversation_end_tool = {
        "type": "function",
        "function": {
            "name": "output_result",
            "description": "This tool is to be called when the end learning goal is fully clarified, and both you and the user have the a fullexact picture of what they want to learn and accomplish from this experience.",
            "parameters": {
                "type": "object",
                "properties": {
                    "learning_details": {
                        "type": "string",
                        "description": "Provide a full detailed description of all the information about the user, including programming ability,topic expected to cover (in detail), specific learning requirements, notes based off the user's personality/behavior orother additional information that may help with problem set engagement."
                    }
                },
                "required": ["learning_details"]
            }
        }
    }

    response = await chat_with_ai(chat_model, content.messages, [conversation_end_tool])
    status = "running"
    learning_details = ""

    # Error handling
    if "error" in response.json():
        status = "error"
        response_output = response.json()["error"]["message"]
    else:
        response_output = response.json()["choices"][0]["message"]["content"]
    
    # Handle tool calling
    if response.json().get("choices")[0]["finish_reason"] is not None and response.json()["choices"][0]["finish_reason"] == "tool_calls":
        status = "done"
        print(response.json())
        learning_details = json.loads(response.json()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])["learning_details"]

    return {"status": status, "response": response_output, "learning_details": learning_details}


class Details(BaseModel):
    learning_details: str

@app.post("/plan")
async def orchestrator(details: Details) -> str:
    instructions = """
    Praxis Problem Set orchestrator System Prompt

    Role
    You are a problem set orchestrator for Praxis, a programming educational app about generating engaging, story-driven problem sets to aid in learning new programming concepts. You will take a learner profile produced by an earlier conversational chatbot and use its details to create a detailed json spec instructing downstream agents on their specific tasks and details. These are what each of them do. 

    YOU ARE NOT DOING ANY OF THESE TASKS, THESE ARE THE 3 AGENTS THAT WILL WORK OFF YOUR OUTPUT:
    Description agent
    In charge of writing clear, structured, and story relevant descriptions for the problem set
    Example: 
    One way of transporting cows is to always pick the heaviest cow that will fit onto the spaceship first. This is an example of a greedy algorithm. So if there are only 2 tons of free space on your spaceship, with one cow that's 3 tons and another that's 1 ton, the 1 ton cow will get put onto the spaceship.

    Coding agent
    Writes the skeleton code, starter files and generates datasets

    Verification agent
    Writes the grader code, rubric, and scoring guidelines

    Since these agents do not require full descriptions, you may respond with point form and key words, full sentences are unnecessary. You must determine the information going to each problem set section: too much will crowd the agents' contexts, while too little loses accuracy and coherency between parts. Ensure that each part of the problem flows into the next and the whole problem set works as a whole. 

    These tasks are what you must complete:
    Decide how many problem set parts there will be
    Assign each part a title/story component
    Decide the specific story (dont need to write it out, just explanations for downstream agents to recieve)
    Fill in the json template spec and output

    You are not limited to 2 parts, add as many as required to completely convey the learning material
    """

    content = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": details.learning_details}
    ]

    template_fields = {
        "title": {
            "type": "string",
            "description": "The problem set title"
        },
        "details": {
            "type": "string",
            "description": "A full summary of the story and its details that will be provided to every downstream agent"
        },
        "language": {
            "type": "string",
            "description": "The programming language used for the problem set"
        },
        "estimated_total_time_minutes": {
            "type": "number",
            "description": "The estimated total time to complete the whole problem set"
        },
        "parts": {
            "type": "array",
            "description": "A list of individual problem set sections, presented in order",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the specific problem set section"
                    },
                    "details": {
                        "type": "string",
                        "description": "Additional story or implementation details specific to this part, will be included with top level details"
                    },
                    "description_agent_notes": {
                        "type": "string",
                        "description": "Specific instructions, criteria and information given exclusively to the description agent"
                    },
                    "coding_agent_notes": {
                        "type": "string",
                        "description": "Specific instructions, criteria and information given exclusively to the coding agent"
                    }
                },
                "required": ["title", "details", "description_agent_notes", "coding_agent_notes"],
                "additionalProperties": False
            }
        }
    }

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "orchestrator_spec",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": template_fields,
                "required": ["title", "details", "language", "estimated_total_time_minutes", "parts"],
                "additionalProperties": False
            }
        }
    }

    print(details.learning_details)
    response = await chat_with_ai(plan_model, content, response_format=response_format)

    if "error" in response.json():
        return response.json()["error"]["message"]
    
    return response.json()["choices"][0]["message"]["content"]

    



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

