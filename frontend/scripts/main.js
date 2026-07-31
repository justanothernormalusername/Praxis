const inputBox = document.querySelector("#user-input");
const button = document.querySelector(".send-button");
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
    const chatMessagesDiv = document.querySelector(".chat-messages");
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

let downloadButton = document.querySelector(".popup button")
downloadButton.addEventListener("click", download)

let buttonSFX = new Audio("/static/buttonSFX.ogg")
console.log(buttonSFX.src)
async function download() {
    buttonSFX.play()
}





// Backend connection!
// code rewritten from backend/client.py

let instructions = "You are a model deployed as part of a learning app called Praxis. The learning app specifically focuses on programming, by generating engaging, stylized, homework like problem sets to exercise and teach techniques and content. The user will typically come in with only a vague idea of what they want to accomplish or learn, and your goal is to clarify the user's end learning goal and preference as accurately and consise as possible. The topic must be narrow enough to fit into a simple problem set, for example: a specific algorithm, an introduction to an advanced concept. Whole units or subfields are too vague. You need to make sure the content fits the experience of the user so previous knowledge must be clarified. For learning preference, the style of the problem set (narrative, storytelling, real-world, implementation, interview, etc.) must also be clarified. You are the first interaction the user will experience on this app. This means asking clarifying questions and suggesting options that may be helpful for the user to organize their thoughts. The chat between you and the user should stay friendly and conversational. This means that responses should not be structured in lists, bullets or charts, etc. Keep responses consise in sentence form, and questions should only be asked one at a time. Suggestions can be made, such as suggesting information to provide, and this can include more than one request. All in all, the secondary goal is to chat with the user and keep the enviornment approachable and friendly, making sure not to overwhelm the user with information and questions. Lastly, before finalizing the conversation, ask a final confirmation with all the information you have to ensure no assumptions are being made and everything is accurate. This way the user can correct any invalid information.";

let messages = [
    {"role": "system", "content": instructions},
    {"role": "assistant", "content": "Hi I'm Praxis, how can I help?"}
];

async function chat(message) {
    chatOpen = false;

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

    displayMessage("ai-message", aiMessage);

    if (reply["status"] !== "done") {
        chatOpen = true;
    }
    else {
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

        return await response.json();
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

        return await response;
    }

    let spec = await plan(learningDetailsInput);
    console.log(spec);

    let psetBuild = await build(spec);
    console.log(psetBuild);
    
    let psetFile = await generate(psetBuild);
    console.log(psetFile);

    // Display and download psetFile
}
