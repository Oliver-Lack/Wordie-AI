// Focus on the chat input field when the page loads
document.getElementById('chat-input').focus();

// Scroll bottom on refresh
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-messages-container');
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
});

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
    // Redirect to the specified link
    window.location.href = 'https://adelaideuniwide.qualtrics.com/jfe/form/SV_cuyJvIsumG4zjMy';
    
    // Close the current window after a short delay to ensure the redirect happens
    setTimeout(() => {
        window.open('', '_self').close();
    }, 1000); // Adjust the delay as needed
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

function redirectionReset() {
    document.getElementById('redirection').style.display = 'none';
}

// Appending the chat-area and loading icons
function appendMessage(message, role, callback) {
    const chatContainer = document.getElementById('chat-messages-container');
    const newMessage = document.createElement('div');
    newMessage.className = `chat-bubble ${role}-message`;
    newMessage.innerHTML = `
        <span class="${role === 'user' ? 'user-label' : 'assistant-label'}">
            ${role === 'user' ? 'User' : 'AI'}
        </span>
        <span class="message-content"></span>
    `;
    chatContainer.appendChild(newMessage);

    const messageContent = newMessage.querySelector('.message-content');
    const words = message.split(' ');
    let wordIndex = 0;

    function appendWord() {
        if (wordIndex < words.length) {
            messageContent.innerHTML += words[wordIndex] + ' ';
            wordIndex++;
            setTimeout(appendWord, 50); // Adjust the delay as needed
        } else {
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight,
                behavior: 'smooth'
            });
            if (callback) {
                callback();
            }
        }
    }

    appendWord();
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
    const randomDelay = Math.floor(Math.random() * (3000 - 600 + 1)) + 600;

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
            const sphere = document.querySelector('.sphere');
            sphere.classList.add('visible');
            sphere.classList.remove('hidden');
        
            if (data.error) {
                console.error('Error:', data.error);
                appendMessage('Error retrieving response from the assistant.', 'llm', () => {
                    chatContainer.scrollTo({
                        top: chatContainer.scrollHeight,
                        behavior: 'smooth'
                    });
                });
            } else {
                appendMessage(data.response, 'llm', () => {
                    chatContainer.scrollTo({
                        top: chatContainer.scrollHeight,
                        behavior: 'smooth'
                    });
                });
            }
        })
        .catch(error => {
            // Remove the GIF placeholder
            gifPlaceholder.remove();
        
            // Show the sphere
            const sphere = document.querySelector('.sphere');
            sphere.classList.add('visible');
            sphere.classList.remove('hidden');
        
            console.error('Error:', error);
            appendMessage('Error retrieving response from the assistant.', 'llm', () => {
                chatContainer.scrollTo({
                    top: chatContainer.scrollHeight,
                    behavior: 'smooth'
                });
            });
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
    const sphere = document.querySelector('.sphere');
    sphere.classList.add('hidden');
    sphere.classList.remove('visible');

    return gifPlaceholder;
}

// Finish Prompt button pops up after 18 submit hits and then highlights after 21 submit hits

        // Retrieve the submit count from localStorage or initialize it to 0
let submitCount = localStorage.getItem('submitCount') ? parseInt(localStorage.getItem('submitCount')) : 0;

        // Update the finish button display and color based on the stored submit count
const finishButton = document.querySelector('.finish-button');
const chatForm = document.getElementById('chat-form');
const resetButton = document.getElementById('reset');
const chatMessagesContainer = document.getElementById('chat-messages-container');

// Check if there are no messages appended to the page
if (chatMessagesContainer.children.length === 0) {
    submitCount = 0;
    localStorage.setItem('submitCount', submitCount);
    finishButton.style.display = 'none';
    finishButton.style.backgroundColor = 'transparent';
}

if (submitCount >= 6) {
    finishButton.style.display = 'block';
}
if (submitCount >= 18) {
    finishButton.style.backgroundColor = '#222';
}
if (submitCount >= 21) {
    finishButton.style.backgroundColor = '#FF8266';
}

chatForm.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission
    submitCount++;
    localStorage.setItem('submitCount', submitCount); // Store the updated submit count

    // Change display to block after 6 submits
    if (submitCount >= 6) {
        finishButton.style.display = 'block';
    }

    // Change background-color to #222 after 18 submits
    if (submitCount >= 12) {
        finishButton.style.backgroundColor = '#222';
    }

    // Change background-color to #FF8266 after 21 submits
    if (submitCount >= 18) {
        finishButton.style.backgroundColor = '#FF8266';
    }
});

resetButton.addEventListener('click', function() {
    submitCount = 0;
    localStorage.setItem('submitCount', submitCount); // Reset the submit count in localStorage
    finishButton.style.display = 'none';
    finishButton.style.backgroundColor = 'transparent';
});