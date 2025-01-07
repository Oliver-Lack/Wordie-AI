hljs.initHighlightingOnLoad();
document.querySelectorAll('code').forEach(function(block) {
    block.insertAdjacentHTML('beforebegin', '<button class="copy-button" onclick="copyToClipboard(this)">Copy</button>');
});

function copyToClipboard(button) {
    var code = button.nextElementSibling.innerText;
    navigator.clipboard.writeText(code).then(function() {
        button.innerText = "Copied!";
        setTimeout(function() {
            button.innerText = "Copy";
        }, 2000);
    }, function() {
        button.innerText = "Error";
    });
}

function showAlert() {
    alert("Warning: The specified environment variable was not found!");
}

function showQuitPrompt() {
    document.getElementById('quit-prompt').style.display = 'block';
}

function hideQuitPrompt() {
    document.getElementById('quit-prompt').style.display = 'none';
}

function quitStudy() {
    window.close(); // This will close the current window/tab
}

function appendMessage(message, role) {
    const chatContainer = document.getElementById('chat-messages-container');
    const newMessage = document.createElement('div');
    newMessage.className = `chat-bubble ${role}-message`;
    newMessage.innerHTML = `<span class="${role}-label">${role === 'user' ? 'User' : 'AI'}</span>${message}`;
    chatContainer.appendChild(newMessage);
}

document.getElementById('chat-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const inputField = document.getElementById('chat-input');
    const form = event.target;
    const chatMessagesContainer = document.getElementById('chat-messages-container');
    
    // Scroll to the bottom of the chat container
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    
    // Append the user message immediately
    const userMessage = document.createElement('div');
    userMessage.className = 'chat-bubble user-message';
    userMessage.innerHTML = '<span class="user-label">User</span>' + inputField.value;
    chatMessagesContainer.appendChild(userMessage);

    // Create a container for the assistant's response
    const assistantResponseContainer = document.createElement('div');
    assistantResponseContainer.className = 'chat-bubble llm-message';
    assistantResponseContainer.innerHTML = '<span class="assistant-label">AI</span>';
    chatMessagesContainer.appendChild(assistantResponseContainer);

    // Create and append the loading indicator inside the assistant's response container
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'loading-indicator';
    loadingIndicator.className = 'loading';
    loadingIndicator.innerHTML = '<span></span><span></span><span></span>';
    assistantResponseContainer.appendChild(loadingIndicator);

    // Generate a random wait time between 2 and 6 seconds
    const waitTime = Math.floor(Math.random() * 2500) + 600;

    setTimeout(() => {
        fetch(form.action, {
            method: form.method,
            body: new FormData(form)
        }).then(response => response.text())
          .then(html => {
              const parser = new DOMParser();
              const doc = parser.parseFromString(html, 'text/html');
              const newMessages = doc.getElementById('chat-messages-container').innerHTML;
              document.getElementById('chat-messages-container').innerHTML = newMessages;
              inputField.value = '';

              // Remove the loading indicator
              loadingIndicator.remove();

          });
    }, waitTime);
});