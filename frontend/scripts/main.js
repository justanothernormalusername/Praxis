const inputBox = document.querySelector("#user-input");
const button = document.querySelector(".send-button");

let chatOpen = true;

function send() {
    // Only processes button press when chat is open (ai not answering)
    if (chatOpen) {
        let message = inputBox.value.trim();
        if (message != "") {
            // Reset chatbox expansion
            inputBox.style.height = "";
            
            inputBox.value = "";

            // Message creation
            const para = document.createElement("p");
            const node = document.createTextNode(message);

            const div = document.createElement("div");
            div.classList.add("user-message");

            para.appendChild(node);
            div.appendChild(para);
            const chatMessagesDiv = document.querySelector(".chat-messages");
            chatMessagesDiv.appendChild(div);

            // Scroll to bottom
            chatMessagesDiv.scroll({
                behavior: "smooth",
                top: chatMessagesDiv.scrollHeight
            });


            chatOpen = false;
            // query backend
            chatOpen = true;
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
console.log(heightLimit)
inputBox.addEventListener("input", (event) => {
    const chatboxDiv = inputBox.parentElement;
    inputBox.style.height = "";
    inputBox.style.height = Math.min(inputBox.scrollHeight, heightLimit) + "px";
})

// Send button functionality
button.addEventListener("click", send);

