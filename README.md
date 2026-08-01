# Praxis
Welcome to the Praxis learning app! This is a project I created to gain experience with AI APIs and frontend development. Also for Horizons Polaris!

## Experience it!
Should be live at the link https://praxis.macrus.hackclub.app!

## What does it do?
Praxis is a personal learning app for programming. It teaches you specific programming concepts using a [Socratic teaching model](https://en.wikipedia.org/wiki/Socratic_method): A method of instruction where the student discovers the answers themselves!

1. The user starts by interacting with the chatbot to determine what they want to learn. The chatbot uses a tool call to end the chat and start generation once it has a clear picture of the learning onjective. 

2. The chat summary/learning objective is sent to the orchestrator agent, which generates a full spec for the writer and coder agents. 

3. The spec is split into parts, where the writer writes each description first, before the coder recieves the spec and writes the skeleton code. 

4. Each JSON is compressed into files then compiled into a .zip file for the user to download. 

## How was this made?
Frontend made with simple JavaScript, CSS, and HTML. 

Python backend made with the [FastAPI](https://fastapi.tiangolo.com/) web framework using [uvicorn](https://uvicorn.dev/). 

AI uses an [openrouter](https://openrouter.ai/) key from [Hack Club AI](https://ai.hackclub.com/). Uses [DeepSeek V4 Flash](https://openrouter.ai/deepseek/deepseek-v4-flash) for chat, Anthropic's [Claude Sonnet 5](https://openrouter.ai/anthropic/claude-sonnet-5) for planning, and Z.ai's [GLM 5.2](https://openrouter.ai/z-ai/glm-5.2) for code and description writing. 

[Ubuntu](https://ubuntu.com/) Linux web server howsted with [systemd](https://systemd.io/) on [Hack Club Nest](https://hackclub.app/)!

### AI DISCLOSURE
Minimal AI generated code; I specifically requested the AI to never write any code, only give keywords for me to Google and formulate a solution. 

No AI code was copied and pasted - *made sure to type everything out by hand to facilitate learning*! 

Used Claude Sonnet with project planning and learning syntax. It guided me through learning HTML, CSS, JS, and the various Python libraries. 

Some code (ex. CSS animations) were typed out from the built-in Google AI after searching. 

### Credits
Thanks to:
[ivanding3](https://github.com/ivanding3), [ProbablyaDoor](https://github.com/ProbablyaDoor), [A-Random-Panda](https://github.com/A-Random-Panda), [zhang-shuning](https://github.com/zhang-shuning), and dedalpaca for testing the site!