import requests
from collections.abc import Callable
from typing import Any
import inspect
import shlex
import json
import asyncio

class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, Callable[..., Any]] = {}

    def register(self, prefix: str) -> Callable[..., Any]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if prefix in self._commands:
                raise ValueError(f"Command '{prefix}' already registered")
            self._commands[prefix] = func
            return func
        return decorator

    def parse(self, command: str) -> str:
        segmented_cmd = shlex.split(command)
        if not segmented_cmd:
            return "No command entered"
        func = self._commands.get(segmented_cmd[0])
        if func is None:
            return "Command not found"
        
        args = segmented_cmd[1:]
        try:
            inspect.signature(func).bind(*args)
        except TypeError:
            return "Wrong number of arguments for this command"

        try:
            func(*args)
            return ""
        except Exception as e:
            return f"Error running command: {e}"
    
    def get_commands(self) -> set:
        return set(self._commands.keys())
        

async def deploy_agents(spec: dict) -> dict:
    """
    Returns a dict in this format:
    {
        "title": str,
        "details": str,
        "language": str,
        "estimated_total_time_minutes": int,
        "parts": [
            {
                "title": str,
                "details": str,
                "description": str,
                "code": str
            },
            {
                "title": str,
                "details": str,
                "description": str,
                "code": str
            },
            ...
        ]
    }
    """
    def call_agents() -> dict:
        def make_request(type: str, request_json: dict) -> dict:
            if type == "write":
                return requests.post("http://127.0.0.1:8000/write", json=request_json).json()
            elif type == "code":
                return requests.post("http://127.0.0.1:8000/code", json=request_json).json()
            else:
                raise TypeError("Type argument must be \"write\" or \"code\"")

        section_output = {
            "write": [], 
            "code": []
        }

        for section in spec["parts"]:
            agent_request_json = {
                "title": spec["title"],
                "details": spec["details"],
                "language": spec["language"],
                "part_title": section["title"],
                "writer_details": section["description_agent_notes"],
                "coder_details": section["coding_agent_notes"]
            }

            section_output["write"].append(asyncio.to_thread(make_request, "write", agent_request_json))
            section_output["code"].append(asyncio.to_thread(make_request, "code", agent_request_json))
        return section_output

    # Function outputs dict of lists of coroutines
    coroutine_dict = call_agents()

    completed_write, completed_code = await asyncio.gather(
        asyncio.gather(*coroutine_dict["write"]),
        asyncio.gather(*coroutine_dict["code"]),
    )

    return {
        "title": spec["title"],
        "details": spec["details"],
        "language": spec["language"],
        "estimated_total_time_minutes": spec["estimated_total_time_minutes"],
        "parts": [
            {
                "title": spec["parts"][i]["title"],
                "details": spec["parts"][i]["details"],
                "description": completed_write[i],
                "code": completed_code[i]
            }
            for i in range(len(spec["parts"]))
        ]
    }


# async def deploy_agents(spec: dict) -> dict:
    """
    Returns a dict in this format:
    {
        "title": str,
        "details": str,
        "language": str,
        "estimated_total_time_minutes": int,
        "parts": [
            {
                "title": str,
                "details": str,
                "write": requests.models.Response,
                "code": requests.models.Response
            },
            {
                "title": str,
                "details": str,
                "write": requests.models.Response,
                "code": requests.models.Response
            },
            ...
        ]
    }
    """

    return {
        "title": spec["title"],
        "details": spec["details"],
        "language": spec["language"],
        "estimated_total_time_minutes": spec["estimated_total_time_minutes"],
        "parts": [
            {
                "title": spec["parts"][i]["title"],
                "details": spec["parts"][i]["details"],
                "write": completed_write[i],
                "code": completed_code[i]
            }
            for i in range(len(spec["parts"]))
        ]
    }

registry = CommandRegistry()

@registry.register("clist")
def clist() -> None:
    print(registry.get_commands())

@registry.register("plan")
def plan(learning_details: str) -> dict:
    spec = json.loads(requests.post("http://127.0.0.1:8000/plan", json={"learning_details": learning_details}).json())
    return spec

@registry.register("build")
def build(spec: dict) -> None:
    # Only when running default admin command
    if not spec:
        with open("test_spec.json", "r") as file:
            spec = json.loads(file.read())
    
    # build_output = asyncio.run(deploy_agents(spec))
    build_output = requests.post("http://127.0.0.1:8000/build", json=spec).json()

    with open("out.txt", "w", encoding="utf-8") as file:
        json.dump(build_output, file, indent=4, ensure_ascii=False)

    print(build_output)

@registry.register("generate")
def generate() -> None:
    with open("out.txt", "r", encoding="utf-8") as out:
        with open("out.py", "w", encoding="utf-8") as file:
            file.write(json.loads(out.read())["code"])

instructions = "You are a model deployed as part of a learning app called Praxis. The learning app specifically focuses on programming, by generating engaging, stylized, homework like problem sets to exercise and teach techniques and content. The user will typically come in with only a vague idea of what they want to accomplish or learn, and your goal is to clarify the user's end learning goal and preference as accurately and consise as possible. The topic must be narrow enough to fit into a simple problem set, for example: a specific algorithm, an introduction to an advanced concept. Whole units or subfields are too vague. You need to make sure the content fits the experience of the user so previous knowledge must be clarified. For learning preference, the style of the problem set (narrative, storytelling, real-world, implementation, interview, etc.) must also be clarified. You are the first interaction the user will experience on this app. This means asking clarifying questions and suggesting options that may be helpful for the user to organize their thoughts. The chat between you and the user should stay friendly and conversational. This means that responses should not be structured in lists, bullets or charts, etc. Keep responses consise in sentence form, and questions should only be asked one at a time. Suggestions can be made, such as suggesting information to provide, and this can include more than one request. All in all, the secondary goal is to chat with the user and keep the enviornment approachable and friendly, making sure not to overwhelm the user with information and questions. Lastly, before finalizing the conversation, ask a final confirmation with all the information you have to ensure no assumptions are being made and everything is accurate. This way the user can correct any invalid information."

messages = [
    {"role": "system", "content": instructions}
]


# Chat
while True:
    new_message = input()

    if new_message == "cmd":
        command = input("Command: ")
        print(registry.parse(command))
        continue

    messages.append({"role": "user", "content": new_message})

    reply = requests.post("http://127.0.0.1:8000/chat", json={"messages": messages}).json()
    messages.append({"role": "assistant", "content": reply["response"]})

    print(reply["response"])

    if reply["status"] == "done":
        break


# Plan
spec = plan(reply["learning_details"])

print(spec)

# In out.txt
build(spec)

