#these are state variable
#initially needed to know whose portal is that
let username = prompt("Enter your name")

#user name not mentioned then it will be taken as guest
if (!username) username = "Guest"

#currentUser is the person i am selecting to chat them
let currentUser = null

#it is a reference to the timeout used -  typing
let typingTimer = null

#used status indicator such as offline or online
let presenceMap = {}

#create the websocket connection
let ws = new WebSocket("ws://localhost:8000/ws")

#sends the hello handshake protocol to know the username,status presence
ws.onopen = function () {
    ws.send(JSON.stringify({ type: "hello", username: username }))
}

ws.onmessage = function (event) {
    let data = JSON.parse(event.data)

    if (data.type === "presence") {
        presenceMap[data.username] = data.status
        updatePresenceDots()
        return
    }

    if (data.type === "typing") {
        if (data.username === currentUser && data.to === username) {
            let indicator = document.getElementById("typingIndicator")
            if (data.isTyping) {
                indicator.textContent = "typing"
            } else {
                indicator.textContent = ""
            }
        }
        return
    }

    if (data.type === "message") {
        if (data.username === currentUser) {
            document.getElementById("typingIndicator").textContent = ""
        }

        if (
            (data.username === username  && data.to === currentUser) ||
            (data.username === currentUser && data.to === username)
        ) {
            addMessage(data)
        }
    }
}

ws.onclose = function () {
    console.log("WebSocket disconnected")
}

document.getElementById("message").addEventListener("input", function () {
    if (!currentUser) return
    ws.send(JSON.stringify({ type: "typing", username: username, to: currentUser, isTyping: true }))
    clearTimeout(typingTimer)
    typingTimer = setTimeout(() => {
        ws.send(JSON.stringify({ type: "typing", username: username, to: currentUser, isTyping: false }))
    }, 1500)
})

document.getElementById("message").addEventListener("keydown", function (e) {
    if (e.key === "Enter") send()
})

function addMessage(data) {
    let div = document.createElement("div")
    div.className = "message " + (data.username === username ? "sent" : "received")
    div.innerHTML = `
        ${escapeHtml(data.message)}
        <div class="timestamp">${data.timestamp}</div>
    `
    let container = document.getElementById("messages")
    container.appendChild(div)
    container.scrollTop = container.scrollHeight
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
}

function send() {
    if (!currentUser) return
    let input = document.getElementById("message")
    let msg = input.value.trim()
    if (msg === "") return

    ws.send(JSON.stringify({
        type: "message",
        username: username,
        to: currentUser,
        message: msg
    }))

    clearTimeout(typingTimer)
    ws.send(JSON.stringify({ type: "typing", username: username, to: currentUser, isTyping: false }))

    input.value = ""
}

function addUser() {
    let name = prompt("Enter person's name")
    if (!name || name.trim() === "") return
    name = name.trim()

    if (document.querySelector(`.user[data-name="${name}"]`)) {
        alert(`${name} is already in your list.`)
        return
    }

    let div = document.createElement("div")
    div.className = "user"
    div.dataset.name = name

    let dot = document.createElement("span")
    dot.className = "presence " + (presenceMap[name] || "offline")
    dot.title = presenceMap[name] || "offline"

    let label = document.createElement("span")
    label.textContent = name

    div.appendChild(dot)
    div.appendChild(label)
    div.onclick = function () { selectUser(name, div) }

    document.getElementById("users").appendChild(div)
}

function selectUser(name, element) {
    currentUser = name

    let header = document.getElementById("chatHeader")
    header.innerHTML = `${escapeHtml(name)} <span class="typing-text" id="typingIndicator"></span>`

    document.querySelectorAll(".user").forEach(u => u.classList.remove("active"))
    element.classList.add("active")

    loadMessages()
}

async function loadMessages() {
    document.getElementById("messages").innerHTML = ""
    try {
        let response = await fetch(
            `http://localhost:8000/messages?user1=${encodeURIComponent(username)}&user2=${encodeURIComponent(currentUser)}`
        )
        let messages = await response.json()
        messages.forEach(m => addMessage(m))
    } catch (e) {
        console.error("Failed to load messages:", e)
    }
}

function updatePresenceDots() {
    document.querySelectorAll(".user[data-name]").forEach(div => {
        let name = div.dataset.name
        let dot = div.querySelector(".presence")
        if (!dot) return
        let status = presenceMap[name] || "offline"
        dot.className = "presence " + status
        dot.title = status
    })
}
