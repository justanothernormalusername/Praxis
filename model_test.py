from dotenv import load_dotenv
import requests
import os
from pydantic import BaseModel

load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"

# message = "ABC"
model = "anthropic/claude-sonnet-5"

json_template = {
    "title": "Space Cows",
    "introduction": "A colony of Aucks (super-intelligent alien bioengineers) has landed on Earth and has created new species of farm animals! The Aucks are performing their experiments on Earth, and plan on transporting the mutant animals back to their home planet of Aurock. In this problem set, you will implement algorithms to figure out how the aliens should shuttle their experimental animals back across space.",
    "language": "Python 3",
    "estimated_total_time_minutes": 90,
    "parts": [
        {
            "id": 1,
            "section_title": "Greedy Cow Transport",
            "description_details": "Any information (including story outline) you plan to include for any agent working on this part",
            "task": "The user's task - what does the user need to accomplish here?"
        },
        {
            "id": 2,
            "section_title": "",
            "description_details": "",
            "task": ""
        }
    ]
}


with open("prompt_new.txt") as f:
    content = f.read()

# "You are a model deployed as part of a learning app called Praxis. The learning app specifically focuses on programming, by generating engaging, stylized, homework like problem sets to exercise and teach techniques and content. The user will typically come in with only a vague idea of what they want to accomplish or learn, and a previous agent has already clarified the user's end learning goal and preference. Its summary will be provided to you, your goal is to provide a detailed spec to pass onto future agents that will write the exact descriptions, code, story and verification. Answer only in a json format with 4 specific sections: description, code, story and verification. Each will have a part for each section of the final problem set. You will be deciding how many parts the problem set will be, and the general title for each separated section."

messages = [
    {"role": "system", "content": content}
]

tools = []

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

def make_request() -> requests.models.Response:
    return requests.post(
        url = URL,
        headers = {"Authorization": f"Bearer {API_KEY}"},
        json = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "response_format": response_format
        }
    )

# print(make_request().json())


while True:
    new_message = input()
    if not new_message:
        continue
    messages.append({"role": "user", "content": new_message})
    response = make_request()
    print(response.text)
    if "error" in response.json():
        print(response.json()["error"]["message"])
    else:
        print(response.json()["choices"][0]["message"]["content"])
