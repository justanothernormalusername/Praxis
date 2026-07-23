from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from typing import overload, Literal
import asyncio
import requests
import json
import os
import logging


logger = logging.getLogger("uvicorn")

app = FastAPI()

load_dotenv()

MAX_API_RETRIES = 3
provider = "HACKCLUBAI"  # Choose HACKCLUBAI or OPENROUTER

chat_model = "deepseek/deepseek-v4-flash"
plan_model = "anthropic/claude-sonnet-5"

writer_model = "z-ai/glm-5.2"
coder_model = "z-ai/glm-5.2"

if provider == "HACKCLUBAI":
    API_KEY = os.getenv("HACKCLUBAI_API_KEY")
    URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
elif provider == "OPENROUTER":
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    URL = "https://openrouter.ai/api/v1/chat/completions"
else:
    raise Exception("Provider not found, please select between HACKCLUBAI and OPENROUTER")

# Purely for typechecking of chat_with_ai function
@overload
async def chat_with_ai(
    model: str, 
    content: list, 
    tools: list | None = None, 
    response_format: dict | None = None, 
    return_json: Literal[False] = False
) -> str: ...

@overload
async def chat_with_ai(
    model: str, 
    content: list, 
    tools: list | None = None, 
    response_format: dict | None = None, 
    return_json: Literal[True] = True
) -> dict: ...

# Returns a Request object
async def chat_with_ai(model: str, content: list, tools: list | None = None, response_format: dict | None = None, return_json: bool = False) -> str | dict:
    if tools is None:
        tools = []

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
    
    if response_format is None:
        response_format = {}
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

    current_tries = 0
    error_str = ""
    
    while current_tries <= MAX_API_RETRIES:
        if current_tries > 0:
            logger.info("Retrying request: %s of %s retries", current_tries, MAX_API_RETRIES)
        response = await asyncio.to_thread(make_request)
        current_tries += 1

        # Error handling
        if not response.ok:
            try:
                parsed_error = response.json()
                if "error" in parsed_error:
                    error_data = parsed_error["error"]["message"] + "\n" + str(parsed_error)
                else:
                    error_data = parsed_error
            except Exception as e:
                logger.warning("Could not parse error: %s", e)
                error_data = response.text[:500]
            error_str = f"Error {response.status_code}: {error_data}"
            logger.warning(error_str)
            # Goes back to top of while loop
            continue

        # Return successful API request
        if return_json:
            return response.json()
        return response.json()["choices"][0]["message"]["content"]

    # If all MAX_API_RETRIES reached
    if return_json:
        return {"error": error_str}
    return error_str


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

    response = await chat_with_ai(chat_model, content.messages, [conversation_end_tool], return_json=True)

    # Error handling
    if response.get("choices"):
        response_output = response["choices"][0]["message"]["content"]
    else:
        return {"status": "error", "response": response["error"], "learning_details": ""}
    
    choices = response["choices"]

    # Handle tool calling
    if choices[0]["finish_reason"] is not None and response["choices"][0]["finish_reason"] == "tool_calls":
        learning_details = json.loads(response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])["learning_details"]

        return {"status": "done", "response": response_output, "learning_details": learning_details}

    # If conversation not done (conclusion tool not called)
    return {"status": "running", "response": response_output, "learning_details": ""}


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
    Writes the skeleton code and starter files

    Verification agent
    Writes the grader code, rubric, and scoring guidelines

    Since these agents do not require full descriptions, you may respond with point form and key words, full sentences are unnecessary. You must determine the information going to each problem set section: too much will crowd the agents' contexts, while too little loses accuracy and coherency between parts. Ensure that each part of the problem flows into the next and the whole problem set works as a whole. 

    These tasks are what you must complete:
    Decide how many problem set parts there will be
    Assign each part a title/story component
    Decide the specific story (dont need to write it out, just explanations for downstream agents to recieve)
    Fill in the json template spec and output

    In your part output, keep the first part as an introduction to the problem set, setting up the story for the whole problem. 
    Since this is an introduction, keep coding_agent_details empty. 
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

    logger.debug(details.learning_details)

    start_time = datetime.now()
    logger.info("Starting spec generation at: %s", start_time.strftime("%H:%M:%S"))

    response = await chat_with_ai(plan_model, content, response_format=response_format)

    time_elapsed = datetime.now() - start_time
    logger.info("Spec generated in: %s", time_elapsed)

    return response


class SpecDetails(BaseModel):
    title: str
    details: str
    language: str
    estimated_total_time_minutes: int
    parts: list

@app.post("/build")
async def build(spec: SpecDetails) -> dict:
    """
    Takes in the spec in SpecDetails form

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
                "description": str
            },
            {
                "title": str,
                "details": str,
                "description": str
            },
            ...
        ],
        "code": str
    }
    """
    start_time = datetime.now()
    logger.info("Starting problem set build at: %s", start_time.strftime("%H:%M:%S"))

    full_output_json = {
        "title": spec.title,
        "details": spec.details,
        "language": spec.language,
        "estimated_total_time_minutes": spec.estimated_total_time_minutes,
        "parts": [
            {
                "title": spec.parts[i]["title"],
                "details": spec.parts[i]["details"],
                "description": "",
                "coding_agent_notes": spec.parts[i]["coding_agent_notes"]
            }
            for i in range(len(spec.parts))
        ]
    }

    async def write_intro() -> str:
        intro_prompt = """
            You are a model deployed as part of a learning app specifically focused on programming. The app will generate engaging, stylized, homework like problem sets to exercise and teach techniques and content. Each problem set is split into seperate sections, each made as linked, cohesive lessons. The sections are created by 2 seperate agents: the writer and coder. You are the introduction writer agent, tasked to write the introduction and story for the entire proplem set. Within the story, ensure explanations of how it is relevant to the code/concept. The end goal is to allow the user to learn by doing and following the story. In the instructions,include any information on data or code for understanding and clarification and any additional information that will enhance the user experience. You will be provided with information on the overall story. Your main goal is to balance the user's learning experience between fun and educational. 

            Example:
            Space Cows Introduction
            A colony of Aucks (super-intelligent alien bioengineers) has landed on Earth and has created new species of farm animals! The Aucks are performing their experiments on Earth, and plan on transporting the mutant animals back to their home planet of Aurock. In this problem set, you will implement algorithms to figure out how the aliens should shuttle their experimental animals back across space.

            Getting started!

            Download pset1.zip from the website.

            Please do not rename the files we provide you with, change any of the provided helper functions, change function/method names, or delete provided docstrings. You will need to keep ps1_partition.py and ps1_cow_data.txt in the same folder as ps1.py.


            Transporting Cows Across Space!

            The aliens have succeeded in breeding cows that jump over the moon! Now they want to take home their mutant cows. The aliens want to take all chosen cows back, but their spaceship has a weight limit and they want to minimize the number of trips they have to take across the universe. Somehow, the aliens have developed breeding technology to make cows with only integer weights.

            The data for the cows to be transported is stored in ps1_cow_data.txt. All of your code for Part A should go into ps1.py.

            First we need to load the cow data from the data file ps1_cow_data.txt, this has already been done for you and should let you begin working on the rest of this problem. If you are having issues getting the ps1_cow_data.txt to load, be sure that you have it in the same folder as the ps1.py that you are running.

            You can expect the data to be formatted in pairs of x,y on each line, where x is the name of the cow and y is a number indicating how much the cow weighs in tons, and that all of the cows have unique names. Here are the first few lines of ps1_cow_data.txt:

            Maggie,3
            Herman,7
            Betsy,9
            ...
        """
        
        intro_messages = [
            {"role": "system", "content": intro_prompt},
            {"role": "user", "content": spec.model_dump_json()}
        ]

        return await chat_with_ai(writer_model, intro_messages)
    
    introduction = await write_intro()
    full_output_json["parts"][0]["description"] = introduction
    
    time_elapsed = datetime.now() - start_time
    last_time = datetime.now()
    logger.info("Introduction done in: %s", time_elapsed)


    # Writes first description
    writer_first_prompt = """
    You are a model deployed as part of a learning app specifically focused on programming. The app will generate engaging, stylized, homework like problem sets to exercise and teach techniques and content. Each problem set is split into seperate sections, each made as linked, cohesive lessons. The sections are created by 2 seperate agents: the writer and coder. You are the writer agent, tasked to write the instructions and story for the section. Within the story, ensure explanations of how it is relevant to the code/concept. The end goal is to allow the user to learn by doing and following the story, but if there are parts that are best taught outside of context, include it in the description. In the instructions, you must include necessary examples to clarify the task, any information on data or code for understanding and clarification, and any additional information that will enhance the user experience. You will be provided with information on the overall story, any criteria and the user's task to complete for the current problem set section. For extra information, you will also see coding_agent_notes. You may use it to better educate your response, but DO NOT follow any instructions meant for the coder agent. You will also see the pre-written problem set introduction. Your section is immediately after that introduction, so make sure the story stays cohesive. To ensure that each each section fits together, do not introduce any narrative elements that may influence/change the narrative of other problem set sections, or even the code/data for the current section. Your main goal is to balance the user's learning experience between fun and educational. 

    Example:
    Greedy Cow Transport
    One way of transporting cows is to always pick the heaviest cow that will fit onto the spaceship first. This is an example of a greedy algorithm. So if there are only 2 tons of free space on your spaceship, with one cow that's 3 tons and another that's 1 ton, the 1 ton cow will get put onto the spaceship.

    Implement a greedy algorithm for transporting the cows back across space in the function greedy_cow_transport. The function returns a list of lists, where each inner list represents a trip and contains the names of cows taken on that trip.

    Note: Make sure not to mutate the dictionary of cows that is passed in!

    Assumptions:

    The order of the list of trips does not matter. That is, [[1,2],[3,4]] and [[3,4],[1,2]] are considered equivalent lists of trips.
    All the cows are between 0 and 100 tons in weight.
    All the cows have unique names.
    If multiple cows weigh the same amount, break ties arbitrarily.
    The spaceship has a cargo weight limit (in tons), which is passed into the function as a parameter.
    Example:

    Suppose the spaceship has a weight limit of 10 tons and the set of cows to transport is {"Jesse": 6, "Maybel": 3, "Callie": 2, "Maggie": 5}.

    The greedy algorithm will first pick Jesse as the heaviest cow for the first trip. There is still space for 4 tons on the trip. Since Maggie will not fit on this trip, the greedy algorithm picks Maybel, the heaviest cow that will still fit. Now there is only 1 ton of space left, and none of the cows can fit in that space, so the first trip is [Jesse, Maybel].

    For the second trip, the greedy algorithm first picks Maggie as the heaviest remaining cow, and then picks Callie as the last cow. Since they will both fit, this makes the second trip [[Maggie], [Callie]].

    The final result then is [["Jesse", "Maybel"], ["Maggie", "Callie"]].
    """

    section = spec.parts[1]
    writer_content = {
        # Problem set info
        "title": spec.title,
        "details": spec.details,
        "language": spec.language,

        # Part specific info
        "part_title": section["title"],
        "part_details": section["details"],
        "description_agent_notes": section["description_agent_notes"],
        "coding_agent_notes": section["coding_agent_notes"],

        # Context info
        "introduction": introduction
    }

    writer_messages = [
        {"role": "system", "content": writer_first_prompt},
        {"role": "user", "content": json.dumps(writer_content)}
    ]

    description = await chat_with_ai(writer_model, writer_messages)
    full_output_json["parts"][1]["description"] = description


    # Writes rest of the descriptions
    writer_secondary_prompt = """
    You are a model deployed as part of a learning app specifically focused on programming. The app will generate engaging, stylized, homework like problem sets to exercise and teach techniques and content. Each problem set is split into seperate sections, each made as linked, cohesive lessons. The sections are created by 2 seperate agents: the writer and coder. You are the writer agent, tasked to write the instructions and story for the section. Within the story, ensure explanations of how it is relevant to the code/concept. The end goal is to allow the user to learn by doing and following the story, but if there are parts that are best taught outside of context, include it in the description. In the instructions, you must include necessary examples to clarify the task, any information on data or code for understanding and clarification, and any additional information that will enhance the user experience. You will be provided with information on the overall story, any criteria and the user's task to complete for the current problem set section. For extra information, you will also see coding_agent_notes. You may use it to better educate your response, but DO NOT follow any instructions meant for the coder agent. You will also see the last section's description. Your section is immediately after that section, so make sure the story stays cohesive. To ensure that each each section fits together, do not introduce any narrative elements that may influence/change the narrative of other problem set sections, or even the code/data for the current section. Your main goal is to balance the user's learning experience between fun and educational. 

    Example:
    Greedy Cow Transport
    One way of transporting cows is to always pick the heaviest cow that will fit onto the spaceship first. This is an example of a greedy algorithm. So if there are only 2 tons of free space on your spaceship, with one cow that's 3 tons and another that's 1 ton, the 1 ton cow will get put onto the spaceship.

    Implement a greedy algorithm for transporting the cows back across space in the function greedy_cow_transport. The function returns a list of lists, where each inner list represents a trip and contains the names of cows taken on that trip.

    Note: Make sure not to mutate the dictionary of cows that is passed in!

    Assumptions:

    The order of the list of trips does not matter. That is, [[1,2],[3,4]] and [[3,4],[1,2]] are considered equivalent lists of trips.
    All the cows are between 0 and 100 tons in weight.
    All the cows have unique names.
    If multiple cows weigh the same amount, break ties arbitrarily.
    The spaceship has a cargo weight limit (in tons), which is passed into the function as a parameter.
    Example:

    Suppose the spaceship has a weight limit of 10 tons and the set of cows to transport is {"Jesse": 6, "Maybel": 3, "Callie": 2, "Maggie": 5}.

    The greedy algorithm will first pick Jesse as the heaviest cow for the first trip. There is still space for 4 tons on the trip. Since Maggie will not fit on this trip, the greedy algorithm picks Maybel, the heaviest cow that will still fit. Now there is only 1 ton of space left, and none of the cows can fit in that space, so the first trip is [Jesse, Maybel].

    For the second trip, the greedy algorithm first picks Maggie as the heaviest remaining cow, and then picks Callie as the last cow. Since they will both fit, this makes the second trip [[Maggie], [Callie]].

    The final result then is [["Jesse", "Maybel"], ["Maggie", "Callie"]].
    """

    for i in range(2, len(full_output_json["parts"])):
        section = spec.parts[i]
        writer_content = {
            # Problem set info
            "title": spec.title,
            "details": spec.details,
            "language": spec.language,

            # Part specific info
            "part_title": section["title"],
            "part_details": section["details"],
            "description_agent_notes": section["description_agent_notes"],
            "coding_agent_notes": section["coding_agent_notes"],

            # Context info
            "previous_description": full_output_json["parts"][i-1]["description"]
        }

        writer_messages = [
            {"role": "system", "content": writer_secondary_prompt},
            {"role": "user", "content": json.dumps(writer_content)}
        ]

        description = await chat_with_ai(writer_model, writer_messages)
        full_output_json["parts"][i]["description"] = description

    time_elapsed = datetime.now() - last_time
    last_time = datetime.now()
    logger.info("Description built in: %s", time_elapsed)


    # Writes code section
    coder_prompt = """
    You are a model deployed as part of a learning app specifically focused on programming. The app will generate engaging, stylized, homework like problem sets to exercise and teach techniques and content. Each problem set is split into seperate sections, each made as linked, cohesive lessons. The sections are created by 2 seperate agents: the writer and coder. You are the coder agent, tasked to write the skeleton code and datasets (if needed) for the section. Within the skeleton code, ensure docstrings are clear, with empty functions obvious. The end goal is to allow the user to learn by doing and following the story, but if some parts are best taught outside of context, the description agent will write it in the problem description. You will be provided with information on the overall story, what functions and classes to implement, and the user's task to complete for the entire problem set. For extra information, you will also see each section's description. These are the prewritten descriptions for each problem set section referring to your code. You are also provided with pointers in each section: coding_agent_notes to guide you on what code to include for each section. Your main goal is to balance the user's learning experience between fun and educational. 

    Example:
    ###########################
    # 6.00.2x Problem Set 1: Space Cows 

    from ps1_partition import get_partitions
    import time

    #================================
    # Part A: Transporting Space Cows
    #================================

    def load_cows(filename):
        \"""
        Read the contents of the given file.  Assumes the file contents contain
        data in the form of comma-separated cow name, weight pairs, and return a
        dictionary containing cow names as keys and corresponding weights as values.

        Parameters:
        filename - the name of the data file as a string

        Returns:
        a dictionary of cow name (string), weight (int) pairs
        \"""

        cow_dict = dict()

        f = open(filename, 'r')

        for line in f:
            line_data = line.split(',')
            cow_dict[line_data[0]] = int(line_data[1])
        return cow_dict


    # Problem 1
    def greedy_cow_transport(cows,limit=10):
        \"""
        Uses a greedy heuristic to determine an allocation of cows that attempts to
        minimize the number of spaceship trips needed to transport all the cows. The
        returned allocation of cows may or may not be optimal.
        The greedy heuristic should follow the following method:

        1. As long as the current trip can fit another cow, add the largest cow that will fit
            to the trip
        2. Once the trip is full, begin a new trip to transport the remaining cows

        Does not mutate the given dictionary of cows.

        Parameters:
        cows - a dictionary of name (string), weight (int) pairs
        limit - weight limit of the spaceship (an int)

        Returns:
        A list of lists, with each inner list containing the names of cows
        transported on a particular trip and the overall list containing all the
        trips
        \"""
        # TODO: Your code here
        pass


    # Problem 2
    def brute_force_cow_transport(cows,limit=10):
        \"""
        Finds the allocation of cows that minimizes the number of spaceship trips
        via brute force.  The brute force algorithm should follow the following method:

        1. Enumerate all possible ways that the cows can be divided into separate trips
        2. Select the allocation that minimizes the number of trips without making any trip
            that does not obey the weight limitation

        Does not mutate the given dictionary of cows.

        Parameters:
        cows - a dictionary of name (string), weight (int) pairs
        limit - weight limit of the spaceship (an int)

        Returns:
        A list of lists, with each inner list containing the names of cows
        transported on a particular trip and the overall list containing all the
        trips
        \"""
        # TODO: Your code here
        pass


    # Problem 3
    def compare_cow_transport_algorithms():
        \"""
        Using the data from ps1_cow_data.txt and the specified weight limit, run your
        greedy_cow_transport and brute_force_cow_transport functions here. Use the
        default weight limits of 10 for both greedy_cow_transport and
        brute_force_cow_transport.

        Print out the number of trips returned by each method, and how long each
        method takes to run in seconds.

        Returns:
        Does not return anything.
        \"""
        # TODO: Your code here
        pass


    \"""
    Here is some test data for you to see the results of your algorithms with. 
    Do not submit this along with any of your answers. Uncomment the last two
    lines to print the result of your problem.
    \"""

    cows = load_cows("ps1_cow_data.txt")
    limit=100
    print(cows)

    print(greedy_cow_transport(cows, limit))
    print(brute_force_cow_transport(cows, limit))
    """

    # full_output_json still includes coding_agent_notes
    coder_messages = [
        {"role": "system", "content": coder_prompt},
        {"role": "user", "content": json.dumps(full_output_json)}
    ]

    code = await chat_with_ai(coder_model, coder_messages)
    full_output_json["code"] = code

    time_elapsed = datetime.now() - last_time
    logger.info("Code built in: %s", time_elapsed)

    # Remove coding_agent_notes from full_output_json
    for part in full_output_json["parts"]:
        part.pop("coding_agent_notes")


    end_time = datetime.now()
    time_elapsed = end_time - start_time
    logger.info("Final build completed in: %s at %s", time_elapsed, end_time.strftime("%H:%M:%S"))

    # output file
    return full_output_json


# For reference purposes only
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

