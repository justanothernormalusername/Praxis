from dotenv import load_dotenv
import requests
import os

load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"

# message = "ABC"
model = "anthropic/claude-sonnet-4.6"

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

def make_request() -> requests.models.Response:
    return requests.post(
        url = URL,
        headers = {"Authorization": f"Bearer {API_KEY}"},
        json = {
            "model": model,
            "messages": messages,
            "tools": tools
        }
    )

# print(make_request().json())


while True:
    new_message = input()
    if not new_message:
        continue
    messages.append({"role": "user", "content": new_message})
    print(make_request().json()["choices"][0]["message"]["content"])
