import requests

instructions = "Start each response with [BOT]"

messages = [
    {"role": "system", "content": instructions}
]

while True:
    new_message = input()
    messages.append({"role": "user", "content": new_message})

    reply = requests.post("http://127.0.0.1:8000", json={"messages": messages}).json()
    messages.append({"role": "assistant", "content": reply["response"]})

    print(reply["response"])

    if reply["status"] == "done":
        break

print(reply)
