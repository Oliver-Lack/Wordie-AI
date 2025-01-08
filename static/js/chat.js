// Focus on the chat input field when the page loads
document.getElementById('chat-input').focus();

// Environment variable alert
function showAlert() {
    alert("Warning: The specified environment variable was not found!");
}

// Quit study popup functions
function showQuitPrompt() {
    document.getElementById('quit-prompt').style.display = 'block';
}

function hideQuitPrompt() {
    document.getElementById('quit-prompt').style.display = 'none';
}

function quitStudy() {
    window.close(); // This will close the current window/tab
}

// Finish study popup functions
function showFinishPrompt() {
    document.getElementById('finish-prompt').style.display = 'block';
}

function hideFinishPrompt() {
    document.getElementById('finish-prompt').style.display = 'none';
}

function finishStudy() {
    document.getElementById('redirection').style.display = 'block';
    document.getElementById('finish-prompt').style.display = 'none';
}

// Appending the chat-area and loading icons
function appendMessage(message, role) {
    const chatContainer = document.getElementById('chat-messages-container');
    const newMessage = document.createElement('div');
    newMessage.className = `chat-bubble ${role}-message`;
    newMessage.innerHTML = `
        <span class="${role === 'user' ? 'user-label' : 'assistant-label'}">
            ${role === 'user' ? 'User' : 'AI'}
        </span>
        <span class="message-content">${message}</span>
    `;
    chatContainer.appendChild(newMessage);
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
}

document.getElementById('chat-form').addEventListener('submit', function(event) {
    event.preventDefault();
    appendUserMessage();
    setTimeout(() => {
        const chatContainer = document.getElementById('chat-messages-container');
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 300); 
});

function appendUserMessage() {
    const inputField = document.getElementById('chat-input');
    const userMessage = inputField.value;

    // Append the user message immediately
    appendMessage(userMessage, 'user');

    // Clear the input field
    inputField.value = '';

    // Generate assistant response with a delay
    generateAssistantResponse(userMessage);
}

function generateAssistantResponse(userMessage) {
    // Insert the GIF placeholder
    const gifPlaceholder = insertLoaderPlaceholder();

    // Generate a random delay between 600ms to 4000ms
    const randomDelay = Math.floor(Math.random() * (5000 - 600 + 1)) + 600;

    // Simulate a delay for the assistant's response
    setTimeout(() => {
        const formData = new FormData();
        formData.append('message', userMessage);

        fetch('/chat', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            // Remove the GIF placeholder
            gifPlaceholder.remove();
        
            // Show the sphere
            document.querySelector('.sphere').classList.remove('hidden');
            
        
            if (data.error) {
                console.error('Error:', data.error);
                appendMessage('Error retrieving response from the assistant.', 'llm');
            } else {
                appendMessage(data.response, 'llm');
            }
        })
        .catch(error => {
            // Remove the GIF placeholder
            gifPlaceholder.remove();
        
            // Show the sphere
            document.querySelector('.sphere').classList.remove('hidden');
        
            console.error('Error:', error);
            appendMessage('Error retrieving response from the assistant.', 'llm');
        });
    }, randomDelay);
}

function insertLoaderPlaceholder() {
    const chatContainer = document.getElementById('chat-messages-container');
    const gifPlaceholder = document.createElement('div');
    gifPlaceholder.className = 'loader-placeholder';
    gifPlaceholder.innerHTML = '<img src="/static/images/sphere2.gif" alt="AI">';
    chatContainer.appendChild(gifPlaceholder);
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });

    // Hide the sphere
    document.querySelector('.sphere').classList.add('hidden');

    return gifPlaceholder;
}