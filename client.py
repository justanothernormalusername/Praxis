import requests

instructions = "You are a model deployed as part of a learning app called Praxis. The learning app specifically focuses on programming, by generating engaging, stylized, homework like problem sets to exercise and teach techniques and content. The user will typically come in with only a vague idea of what they want to accomplish or learn, and your goal is to clarify the user's end learning goal and preference as accurately and consise as possible. The topic must be narrow enough to fit into a simple problem set, for example: a specific algorithm, an introduction to an advanced concept. Whole units or subfields are too vague. You need to make sure the content fits the experience of the user so previous knowledge must be clarified. For learning preference, the style of the problem set (narrative, storytelling, real-world, implementation, interview, etc.) must also be clarified. You are the first interaction the user will experience on this app. This means asking clarifying questions and suggesting options that may be helpful for the user to organize their thoughts. The chat between you and the user should stay friendly and conversational. This means that responses should not be structured in lists, bullets or charts, etc. Keep responses consise in sentence form, and questions should only be asked one at a time. Suggestions can be made, such as suggesting information to provide, and this can include more than one request. All in all, the secondary goal is to chat with the user and keep the enviornment approachable and friendly, making sure not to overwhelm the user with information and questions. Lastly, before finalizing the conversation, ask a final confirmation with all the information you have to ensure no assumptions are being made and everything is accurate. This way the user can correct any invalid information."

messages = [
    {"role": "system", "content": instructions}
]

# Chat
while True:
    new_message = input()
    messages.append({"role": "user", "content": new_message})

    reply = requests.post("http://127.0.0.1:8000/chat", json={"messages": messages}).json()
    messages.append({"role": "assistant", "content": reply["response"]})

    print(reply["response"])

    if reply["status"] == "done":
        break

print(reply)


# Plan
spec = requests.post("http://127.0.0.1:8000/plan", json={"learning_details": reply["learning_details"]}).json()

print(spec)

spec = {
  "title": "Operation Starfall: Async Intelligence Network",
  "parts": [
    {
      "part_number": 1,
      "section_title": "Recruiting the Agents",
      "description": {
        "summary": "Introduce asyncio.gather in its simplest form — running multiple coroutines concurrently and collecting their results as a list. The user should write a basic gather call with 2-3 simple coroutines that return values, and observe that results come back in the order the coroutines were passed, not the order they completed.",
        "concepts": ["asyncio.gather basics", "concurrent coroutine execution", "ordered result collection"],
        "difficulty": "easy"
      },
      "code": {
        "starter_code_needed": True,
        "starter_code_notes": "Provide async functions that simulate agents 'checking in' with asyncio.sleep delays of different lengths and return strings. Leave the gather call for the user to write. Include a main() coroutine scaffold and asyncio.run() call.",
        "solution_notes": "Solution uses asyncio.gather(agent1(), agent2(), agent3()) inside main(), stores result in a variable, and prints each result. Should demonstrate that the list index matches call order, not completion order."
      },
      "story": {
        "theme": "A shadowy intelligence director is assembling a team of covert operatives for a mission. Each agent must radio in their codename and status from across the globe. The director needs all agents checked in before the mission briefing begins.",
        "narrative_hook": "The director cannot afford to call each agent one by one — time is critical. They need all agents reporting simultaneously.",
        "flavor_details": "Agent codenames, exotic locations, radio static delays represented by sleep times"
      },
      "verification": {
        "test_approach": "Run the user's solution and assert the returned list has the correct length, correct string values, and is in the correct order matching gather call order. Also time the execution to confirm concurrency (total time should be close to max sleep, not sum of sleeps).",
        "edge_cases": [],
        "key_assertions": ["result list length equals number of coroutines", "results are in call-order not completion-order", "execution time confirms concurrency"]
      }
    },
    {
      "part_number": 2,
      "section_title": "Parallel Intelligence Gathering",
      "description": {
        "summary": "Extend gather usage by unpacking results and passing coroutines dynamically using the starred unpacking pattern (*list_of_coroutines). The user will generate a list of coroutines programmatically and pass them to gather using the * operator, then map results back to their sources.",
        "concepts": ["dynamic coroutine list creation", "starred unpacking with gather", "mapping results back to inputs"],
        "difficulty": "medium"
      },
      "code": {
        "starter_code_needed": True,
        "starter_code_notes": "Provide a single async coroutine template that takes a target name and a delay, simulating 'intelligence gathered' on that target. Provide a list of target dictionaries. Leave the list comprehension, gather call with unpacking, and result mapping to the user.",
        "solution_notes": "Solution builds a list of coroutines via list comprehension, calls asyncio.gather(*coroutines), then zips or enumerates results with the original targets list to print a report."
      },
      "story": {
        "theme": "The agents have been deployed and are now surveilling multiple enemy targets simultaneously. Each agent reports back intelligence on their assigned target.",
        "narrative_hook": "HQ needs to coordinate surveillance on 5 targets at once. The number of targets may change — the system must be dynamic.",
        "flavor_details": "Target codenames like 'The Broker', 'The Courier', intelligence dossier snippets as return values"
      },
      "verification": {
        "test_approach": "Verify the gather call uses * unpacking on a dynamically built list. Assert results list length matches input list length. Assert each result correctly corresponds to the matching input target by checking content. Timing check for concurrency.",
        "edge_cases": ["empty list of coroutines should return empty list"],
        "key_assertions": ["* unpacking is used", "result count matches input count", "result-to-input mapping is correct"]
      }
    },
    {
      "part_number": 3,
      "section_title": "When Agents Go Dark",
      "description": {
        "summary": "Introduce error handling in asyncio.gather using the return_exceptions=True parameter. The user will learn the difference between default gather behavior (first exception cancels all) versus return_exceptions=True (exceptions are returned as result objects). They must handle a mix of successful results and exception objects in the results list.",
        "concepts": ["return_exceptions=True parameter", "exception objects in results list", "isinstance checks on results", "default gather exception propagation"],
        "difficulty": "medium-hard"
      },
      "code": {
        "starter_code_needed": True,
        "starter_code_notes": "Provide async agent coroutines where some randomly or deterministically raise custom exceptions (e.g., AgentCompromisedException). First ask the user to try gather WITHOUT return_exceptions to observe the failure. Then scaffold a second attempt WITH return_exceptions=True. Leave the result-processing loop to the user.",
        "solution_notes": "Solution demonstrates both behaviors with comments. Final solution uses return_exceptions=True, then iterates results checking isinstance(result, Exception) to separate successful intel from compromised agents, printing a mission status report."
      },
      "story": {
        "theme": "Not all agents make it. Some have been compromised by the enemy and their transmissions are cut off mid-mission. HQ must continue processing intel from surviving agents even when others go dark.",
        "narrative_hook": "A rigid system that crashes when one agent fails is a liability. The director needs a resilient network that reports partial success.",
        "flavor_details": "AgentCompromisedException with agent codename, 'SIGNAL LOST' vs 'INTEL RECEIVED' status outputs"
      },
      "verification": {
        "test_approach": "Two-phase testing. Phase 1: confirm that without return_exceptions, an exception propagates and the program raises. Phase 2: with return_exceptions=True, assert that result list contains both string results and Exception instances, and that the user's processing loop correctly categorizes each. Check the counts of successes vs failures match expected.",
        "edge_cases": ["all agents fail", "all agents succeed", "only one agent fails"],
        "key_assertions": ["return_exceptions=True used", "isinstance(result, Exception) check present", "successful results still extracted correctly", "failed agents identified without crashing"]
      }
    },
    {
      "part_number": 4,
      "section_title": "The Final Extraction",
      "description": {
        "summary": "Capstone challenge combining everything: dynamic coroutine creation, gather with unpacking, return_exceptions=True, result mapping, and a timeout enforced via asyncio.wait_for wrapping the entire gather call. The user must orchestrate a full multi-step mission pipeline where multiple agents run concurrently with a mission time limit.",
        "concepts": ["combining all gather patterns", "asyncio.wait_for for timeout", "nested async orchestration", "full pipeline design"],
        "difficulty": "hard"
      },
      "code": {
        "starter_code_needed": True,
        "starter_code_notes": "Provide the agent coroutine definitions and mission parameters (list of agents with delays and potential failures). Provide a skeleton of the orchestrate_mission() coroutine with TODO comments marking each step. The user must fill in: the gather call with all proper flags, wrapping it with wait_for and a timeout, processing the results, and printing a final mission report summary.",
        "solution_notes": "Solution wraps asyncio.gather(*coroutines, return_exceptions=True) inside asyncio.wait_for(..., timeout=X). Catches asyncio.TimeoutError separately. Processes mixed results. Prints structured report: mission success/failure, agents reporting, agents compromised, mission aborted if timeout."
      },
      "story": {
        "theme": "The climactic extraction mission. All agents must simultaneously retrieve their targets and report back to the extraction point. The operation has a hard time limit — if it takes too long, the entire mission must be aborted before enemy forces arrive.",
        "narrative_hook": "This is it. Every skill the director has learned about running parallel operations, handling failures, and working under time pressure converges in the final extraction.",
        "flavor_details": "Mission debrief report format, dramatic timeout abort message, final tally of successful extractions vs casualties vs aborted mission"
      },
      "verification": {
        "test_approach": "Test three scenarios: (1) all agents succeed within timeout — verify complete success report, (2) some agents fail but mission completes in time — verify partial success report with correct failure identification, (3) mission exceeds timeout — verify TimeoutError is caught and abort message is shown. Assert output structure matches expected report format for each scenario.",
        "edge_cases": ["timeout of 0 (immediate abort)", "single agent mission", "all agents take exactly the timeout duration"],
        "key_assertions": ["asyncio.wait_for used with gather", "return_exceptions=True present", "TimeoutError caught and handled gracefully", "final report distinguishes success/failure/timeout states", "no unhandled exceptions in any scenario"]
      }
    }
  ]
}