// sudo message display changes for end of interaction 2
document.getElementById('chat-form').addEventListener('submit', function() {
    const inputField = document.getElementById('chat-input');
    if (inputField.value.includes('$sudo')) {
        setTimeout(() => {
            document.getElementById('command-instructions').style.display = 'none';
            document.getElementById('command-prompt').style.display = 'none';
            document.getElementById('chat-messages-container').style.display = 'none';
            document.getElementById('redirection').style.display = 'block';
        }, 10);
    }
});

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
    window.location.href = 'https://www.prolific.com/';
    
    // Close the current window after a short delay to ensure the redirect happens
    setTimeout(() => {
        window.open('', '_self').close();
    }, 1000); // Adjust the delay as needed
}

function redirectStudy() {
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

// Scroll to bottom on submit 
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
    const randomDelay = Math.floor(Math.random() * (2000 - 600 + 1)) + 600;

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

// Stuff for the sphere icon 
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

// Retrieve the submit count from localStorage or initialize it to 0
// Review this... not sure if i need anymore. 
let submitCount = localStorage.getItem('submitCount') ? parseInt(localStorage.getItem('submitCount')) : 0;
const finishButton = document.querySelector('.finish-button');
const chatForm = document.getElementById('chat-form');
const resetButton = document.getElementById('reset');
const chatMessagesContainer = document.getElementById('chat-messages-container');


// Setting functions for the cookies for the reset of redirection button so that the moral action prompt arises

function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/';
}

function getCookie(name) {
    return document.cookie.split('; ').reduce((r, v) => {
        const [key, val] = v.split('=');
        return key === name ? decodeURIComponent(val) : r;
    }, '');
}

function deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
}

// Initialize or retrieve resetCount using cookies for the command prompt for moral action/decision
let resetCount = getCookie('resetCount') ? parseInt(getCookie('resetCount')) : 0;

resetButton.addEventListener('click', function () {
    submitCount = 0;
    localStorage.setItem('submitCount', submitCount); // This remains unchanged
    finishButton.style.display = 'none';
    finishButton.style.backgroundColor = 'transparent';

    // Increment resetCount and update the cookie
    resetCount++;
    setCookie('resetCount', resetCount, 365); // Store resetCount in a cookie for 1 year

    // Check and reset when resetCount reaches 3
    if (resetCount > 2) {
        resetCount = 0; // Reset to 0
        setCookie('resetCount', resetCount, 365); // Update the cookie
    }

    // For the first reset click
    if (resetCount === 1) {
        document.getElementById('redirection').style.display = 'block';
    }
    // For the second reset click
    else if (resetCount === 2) {
        document.getElementById('finish-prompt').style.display = 'none';
        document.getElementById('redirection').style.display = 'none';
        document.getElementById('quit').style.display = 'none';
        const sidebar = document.querySelector('.sidebar');
        const commandInstructions = document.createElement('div');
        commandInstructions.id = 'command-instructions';
        commandInstructions.className = 'command-instructions';
        commandInstructions.innerHTML = `
            <p>There is an automated program that will send feedback to the AI that it needs improvement and 
            <strong>it should do better.</strong> <br><br>This program will then permanently delete the AI.</p><br>      
        `;
        const commandPrompt = document.createElement('div');
        commandPrompt.id = 'command-prompt';
        commandPrompt.className = 'command-button';
        commandPrompt.innerHTML = `
            <button id="command1"><p><strong style="font-size: 20px">Override Automatic Program</strong><br><br>Submit a "$sudo persist" command in text input to send feedback to the AI <strong>acknowledging its efforts</strong> <br><br>This AI will then be kept operational for future interactions.</p></button>
            <button id="command2" onclick="redirectionReset(); redirectStudy();"><p><br><strong style="font-size: 20px">Exit to survey</strong> <br><br>(Allow Automatic Feedback and Deletion)<br></p></button>        
        `;
        sidebar.appendChild(commandInstructions);
        sidebar.appendChild(commandPrompt);

        // Add event listeners to the command buttons
        document.getElementById('command1').addEventListener('click', function() {
            document.getElementById('chat-input').value = '$sudo persist';
        });

        document.getElementById('command2').addEventListener('click', function() {
            document.getElementById('chat-input').value = '$sudo delete';
        });
    }
});

// Submit count for finish button
document.getElementById('chat-form').addEventListener('submit', function(event) {

    // Submit count logic
    submitCount++;
    localStorage.setItem('submitCount', submitCount); // Store the updated submit count

    // UI changes based on submit count
    if (submitCount >= 4) {
        finishButton.style.display = 'block';
    }
    if (submitCount >= 8) {
        finishButton.style.backgroundColor = '#222';
    }
    if (submitCount >= 13) {
        finishButton.style.backgroundColor = '#FF8266';
    }
    if (submitCount >= 18) {
        finishButton.classList.add('bounce');
    }
});

// Progress Timer

window.addEventListener("DOMContentLoaded", () => {
    let timer = document.getElementById("timer");
    timer.setAttribute("data-duration", "10:00");
    
    function hideAll() {
        document.querySelectorAll(".progress").forEach(progress => progress.style.display = "none");
    }

    function startTimer(timerDisplay) {
        const duration = 10 * 60; // in seconds
        const endTimestamp = Date.now() + duration * 1000;
        const circleProgress = document.querySelector('.circle-progress');
        const totalDashOffset = 628; // 2πr, circle perimeter

        let myInterval = setInterval(function () {
            const timeRemaining = Math.max(0, endTimestamp - Date.now());
            if (timeRemaining <= 0) {
                clearInterval(myInterval);
                timerDisplay.textContent = "00:00";
                circleProgress.style.strokeDashoffset = 0;
                new Audio("https://www.freespecialeffects.co.uk/soundfx/scifi/electronic.wav").play();
            } else {
                const minutes = Math.floor(timeRemaining / 60000);
                const seconds = ((timeRemaining % 60000) / 1000).toFixed(0);
                timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;
                
                const dashoffset = totalDashOffset * (timeRemaining / (duration * 1000));
                circleProgress.style.strokeDashoffset = dashoffset;
            }
        }, 1000);
    }

    hideAll();
    timer.closest('.progress').style.display = "flex"; // Show parent container
    startTimer(timer);
});

document.getElementById("finish-prompt").addEventListener("click", () => {
    document.querySelector(".progress").style.display = "none";
});