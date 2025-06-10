document.addEventListener("DOMContentLoaded", () => {
	const chatMessages = document.getElementById("chat-messages")
	const userInput = document.getElementById("user-input")
	const sendButton = document.getElementById("send-button")

	const sendMessage = async () => {
		const prompt = userInput.value.trim()
		if (prompt === "") return

		appendMessage(prompt, "user") // Display user's original prompt immediately
		userInput.value = ""

		try {
			const response = await fetch("/chat", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ prompt: prompt }),
			})

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`)
			}

			const data = await response.json()

			// Iterate through the response_steps and append messages
			if (data.response_steps && Array.isArray(data.response_steps)) {
				data.response_steps.forEach((step) => {
					if (step.type === "agent_text") {
						appendMessage(step.content, "agent")
					} else if (step.type === "tool_call") {
						appendToolCall(step.tool_name, step.tool_args, step.tool_output)
					} else if (step.type === "agent_thought") {
						appendThought(step.content)
					} else if (step.type === "error") {
						appendMessage(`Error: ${step.content}`, "agent error")
					}
					// 'user' type is already appended at the beginning of sendMessage
				})
			} else {
				// Fallback for unexpected response structure
				appendMessage("Received unexpected response from agent.", "agent error")
				console.error("Unexpected response structure:", data)
			}
		} catch (error) {
			console.error("Error sending message:", error)
			appendMessage("Error: Could not connect to the agent. Please check the server.", "agent error")
		}
	}

	const appendMessage = (text, sender) => {
		const messageDiv = document.createElement("div")
		messageDiv.classList.add("message", sender)
		messageDiv.textContent = text
		chatMessages.appendChild(messageDiv)
		chatMessages.scrollTop = chatMessages.scrollHeight // Auto-scroll to bottom
	}

	const appendToolCall = (toolName, toolArgs, toolOutput) => {
		const toolCallDiv = document.createElement("div")
		toolCallDiv.classList.add("message", "agent", "tool-call")

		const toolNameHeader = document.createElement("h4")
		toolNameHeader.textContent = `Tool Call: ${toolName}`
		toolCallDiv.appendChild(toolNameHeader)

		const argsHeader = document.createElement("p")
		argsHeader.innerHTML = "<strong>Arguments:</strong>"
		toolCallDiv.appendChild(argsHeader)

		const argsList = document.createElement("ul")
		for (const [key, value] of Object.entries(toolArgs)) {
			const listItem = document.createElement("li")
			listItem.textContent = `${key}: ${value}`
			argsList.appendChild(listItem)
		}
		toolCallDiv.appendChild(argsList)

		const outputHeader = document.createElement("p")
		outputHeader.innerHTML = "<strong>Output:</strong>"
		toolCallDiv.appendChild(outputHeader)

		const outputPre = document.createElement("pre")
		outputPre.textContent = toolOutput
		toolCallDiv.appendChild(outputPre)

		chatMessages.appendChild(toolCallDiv)
		chatMessages.scrollTop = chatMessages.scrollHeight
	}

	const appendThought = (text) => {
		const thoughtDiv = document.createElement("div")
		thoughtDiv.classList.add("message", "agent-thought")
		thoughtDiv.textContent = `Agent Thought: ${text}`
		chatMessages.appendChild(thoughtDiv)
		chatMessages.scrollTop = chatMessages.scrollHeight // Auto-scroll to bottom
	}

	sendButton.addEventListener("click", sendMessage)
	userInput.addEventListener("keypress", (e) => {
		if (e.key === "Enter") {
			sendMessage()
		}
	})
})
