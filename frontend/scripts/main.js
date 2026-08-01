const inputBox = document.querySelector("#user-input");
const button = document.querySelector(".send-button");
const chatMessagesDiv = document.querySelector(".chat-messages");
let chatOpen = true;

function displayMessage(messageType, message) {
    // Message creation
    const para = document.createElement("p");
    const node = document.createTextNode(message);

    const div = document.createElement("div");

    if (messageType === "ai-message") {
        div.classList.add("ai-message");
    }
    else if (messageType === "user-message") {
        div.classList.add("user-message");
    }
    else {
        throw new Error("You didn't define messageType correctly!");
    }

    para.appendChild(node);
    div.appendChild(para);

    chatMessagesDiv.appendChild(div);

    // Scroll to bottom
    chatMessagesDiv.scroll({
        behavior: "smooth",
        top: chatMessagesDiv.scrollHeight
    });
}

function send() {
    // Only processes button press when chat is open (ai not answering)
    if (chatOpen) {
        let message = inputBox.value.trim();
        if (message != "") {
            // Reset chatbox expansion
            inputBox.style.height = "";

            inputBox.value = "";

            displayMessage("user-message", message);

            chat(message);
        }
    }
}

// Enter/shift+enter newline & send input
inputBox.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        send();
    }
});

// Input box auto expand
const heightLimit = document.querySelector(".right-component").offsetHeight * 0.5;
inputBox.addEventListener("input", (event) => {
    const chatboxDiv = inputBox.parentElement;
    inputBox.style.height = "";
    inputBox.style.height = Math.min(inputBox.scrollHeight, heightLimit) + "px";
})

// Send button functionality
button.addEventListener("click", send);



// Backend connection!
// code rewritten from backend/client.py

let instructions = "You are a model deployed as part of a learning app called Praxis. The learning app specifically focuses on programming by generating engaging, stylized, homework-like problem sets to exercise and teach techniques and content. The user will typically come in with only a vague idea of what they want to accomplish or learn, and your goal is to clarify the user's end learning goal as accurately and concisely as possible. The topic must be narrow enough to fit into a simple problem set, for example: a specific algorithm, an introduction to an advanced concept. The topic should not just be 'How to do X'. You need to make sure the content fits the experience of the user, so previous knowledge must be clarified. You need specifics on what level the user is at, including topics they are familiar with and topics they would like to improve on. The style of the problem set will be narrative and story-driven, generated later on, but allow the user to recommend specific story topics. Do not ask for story recommendations. Only accept them if the user specifically provides it. If no story subject is given by the user, disregard and continue with the main objective. You are the first interaction the user will experience on this app. This means asking clarifying questions and suggesting options that may be helpful for the user to organize their thoughts. If the user asks specific programming questions, convert the subject into a problem set topic. Never call the conclusion tool if the learning details are not crystal clear. Never respond with an empty response. The chat between you and the user should stay friendly and conversational. This means that responses should not be structured in lists, bullets, or charts, etc. Keep responses concise in sentence form, and do not overwhelm the user with questions. All in all, the secondary goal is to chat with the user and keep the environment approachable and friendly, making sure not to overwhelm the user with information and questions. Lastly, before finalizing the conversation, ask a final confirmation with all the information you have to ensure no assumptions are being made and everything is accurate. This way the user can correct any invalid information.";

let messages = [
    {"role": "system", "content": instructions},
    {"role": "assistant", "content": "Hi I'm Praxis, how can I help?"}
];

async function chat(message) {
    chatOpen = false;
    loadDots = document.createElement("div");
    loadDots.classList.add("typing-indicator");

    dot = document.createElement("span");
    loadDots.appendChild(dot);
    dot = document.createElement("span");
    loadDots.appendChild(dot);
    dot = document.createElement("span");
    loadDots.appendChild(dot);

    chatMessagesDiv.appendChild(loadDots);

    // Scroll to bottom
    chatMessagesDiv.scroll({
        behavior: "smooth",
        top: chatMessagesDiv.scrollHeight
    });

    messages.push({"role": "user", "content": message});

    let reply = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"  // Tells the server that data is JSON
        },
        body: JSON.stringify({"messages": messages})
    });

    reply = await reply.json();
    let aiMessage = reply["response"];
    messages.push({"role": "assistant", "content": aiMessage});

    loadDots.remove();
    

    if (reply["status"] !== "done") {
        displayMessage("ai-message", aiMessage);
        chatOpen = true;
    }
    else {
        // Hard-coded ai response when tool called
        displayMessage("ai-message", "Starting problem set creation!");

        // Display loading ui popup
        let popupOverlay = document.querySelector(".popup-overlay");
        let loadingScreen = document.querySelector(".loading-screen");
        popupOverlay.style.display = "block";
        loadingScreen.style.display = "block";

        compile(reply["learning_details"]);
    }
    return reply;
}



// Compiles problem set with learning details and displays download
async function compile(learningDetailsInput) {

    // Requests spec generation from chat output (learningDetails) and returns full spec
    async function plan(learningDetails) {
        let response = await fetch("/plan", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"learning_details": learningDetails})
        });

        let spec = await response.json();

        return spec;
    }

    // Requests problem set build from compiled spec and returns full json
    async function build(spec) {
        let response = await fetch("/build", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: spec
        });
        let {task_id} = await response.json();

        // Ping server until build finishes
        return new Promise((resolve) => {
            let interval = setInterval(async () => {
                let statusResponse = await fetch(`/status/${task_id}`);
                let statusData = await statusResponse.json();

                if (statusData["status"] === "done") {
                    clearInterval(interval);
                    resolve(statusData["result"]);
                }
            }, 5000);  // Pings every 5 seconds
        });
    }

    // Requests pset zip construction from full pset json
    async function generate(fullJSON) {
        let response = await fetch("/generate", {
            method: "POST", 
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"full_output_json": fullJSON})
        });

        return await response.arrayBuffer();
    }

    let spec = await plan(learningDetailsInput);

    let psetBuild = await build(spec);
    
    let psetFile = await generate(psetBuild);

    // Preparing binary zip for download
    let blob = new Blob([psetFile], {
        type: "application/zip"
    });
    let downloadURL = URL.createObjectURL(blob);

    // Hide loading popup
    let loadingScreen = document.querySelector(".loading-screen");
    loadingScreen.style.display = "none";

    // Display download popup
    let popup = document.querySelector(".popup");
    popup.style.display = "block";

    // Download button functionality
    let downloadButton = document.querySelector(".popup button");
    downloadButton.addEventListener("click", download);

    // Button sound effect
    let buttonSFX = new Audio("/static/buttonSFX.ogg");
    // Runs once user clicks download button
    async function download() {
        buttonSFX.play();

        // Temporary anchor to trigger save dialog
        const link = document.createElement("a");
        link.href = downloadURL;
        link.download = "pset.zip";

        // Trigger download
        link.click();
    }
}
