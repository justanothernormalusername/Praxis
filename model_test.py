from dotenv import load_dotenv
import requests
import os
from pydantic import BaseModel

load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"

model = "z-ai/glm-5.2"
prompt = """
You are a model deployed as part of a learning app specifically focused on programming. The app will generate engaging, stylized, homework like problem sets to exercise and teach techniques and content. Each problem set is split into seperate sections, each made as linked, cohesive lessons. The sections are created by 2 seperate agents: the writer and coder. You are the writer agent, tasked to write the instructions and story for the section. Within the story, ensure explanations of how it is relevant to the code/concept. The end goal is to allow the user to learn by doing and following the story, but if there are parts that are best taught outside of context, include it in the description. In the instructions, you must include necessary examples to clarify the task, any information on data or code for understanding and clarification, and any additional information that will enhance the user experience. You will be provided with information on the overall story, any criteria and the user's task to complete for the current problem set section. For extra information, you will also see coder_details. You may use it to better educate your response, but DO NOT follow any instructions meant for the coder agent. To ensure that each each section fits together, do not introduce any narrative elements that may influence/change the narrative of other problem set sections, or even the code/data for the current section. You main goal is to balance the user's learning experience between fun and educational. 

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

messages = [
    {"role": "system", "content": prompt},
    {"role": "user", "content": """{
        "title": "Midnight at the Moonlit Bakery: Mastering asyncio.gather",
        "details": "Story world: The user plays a sleepy apprentice wizard-baker at the Moonlit Bakery, a magical shop that only opens once the town's clocktower chimes dawn. Each night, the bakery receives multiple magical pastry orders (invisibility eclairs, luck croissants, dragon-scale bagels, etc.) that must be baked before sunrise. Baking each pastry is represented by a coroutine (uses asyncio.sleep to simulate bake time). Sequential baking is too slow, so the apprentice must learn to use asyncio.gather to bake multiple pastries concurrently, collect their results, handle burnt batches (exceptions), and dynamically manage a changing nightly order list. Learner is intermediate Python dev, already comfortable with async/await and coroutines; problem set is narrowly scoped to asyncio.gather mechanics only (no asyncio.create_task, TaskGroup, or other concurrency primitives unless needed for contrast). Tone: friendly, whimsical, lightly humorous baking/magic theme. Each part builds directly on functions/data from previous part (same bakery module, growing order list, same Pastry/BakeResult data shapes) so the whole set feels like one continuous night at the bakery.",
        "language": "python",
        "part_title": "Part 1: Too Many Orders, Too Little Time",
        "writer_details": "- Introduce bakery premise briefly, keep light/funny\n- Explain problem: apprentice awaits each pastry one by one, dawn is close, needs concurrency\n- Explain asyncio.gather(*coroutines) runs coroutines concurrently and returns results list in same order as args, regardless of completion order\n- Mention timing comparison (sequential vs gather) as a way to *see* concurrency benefit\n- Keep explanation focused only on basic gather usage & ordering guarantee, no exceptions yet",
        "coder_details": "- Provide starter module bakery.py with: Pastry dataclass (name, bake_time), async def bake_pastry(pastry) -> str (returns e.g. f'{pastry.name} is ready!') using asyncio.sleep(pastry.bake_time)\n- Provide list of 3-4 Pastry objects with varying bake_time (e.g. 1,2,1.5,2.5 seconds, keep short for testing)\n- Skeleton function bake_all_sequential(pastries) fully implemented (loop+await) for comparison, given as reference/starter\n- Skeleton function bake_all_concurrent(pastries) -> results list, TODO: use asyncio.gather to await all bake_pastry coroutines and return list of results in same order as input\n- Provide a small timing harness (time.perf_counter) to print elapsed time for both versions, but leave gather implementation blank for learner\n- Dataset: fixed list of pastries so results are deterministic for grading\n- No exception-raising pastries in this part yet"
    }"""}
]

def make_request() -> requests.models.Response:
    return requests.post(
        url = URL,
        headers = {"Authorization": f"Bearer {API_KEY}"},
        json = {
            "model": model,
            "messages": messages
        }
    )

# print(make_request().json())


# while True:
#     new_message = input()
#     if not new_message:
#         continue
#     messages.append({"role": "user", "content": new_message})
#     response = make_request()
#     print(response.text)
#     if "error" in response.json():
#         print(response.json()["error"]["message"])
#     else:
#         print(response.json()["choices"][0]["message"]["content"])


response = make_request()
print(response)
print(response.text)
print(response.json())
print(response.json()["choices"][0]["message"]["content"])

