document.addEventListener('DOMContentLoaded', () => {
    const activeForm = localStorage.getItem('activeForm') || 'about';
    showForm(activeForm);
    listJsonFiles();
    populateAgentDropdown();
    listPasswords();
});

function createJsonFile() {
    const form = document.getElementById('agent-form');
    const data = new FormData(form);
    const filename = data.get('json-filename').trim();

    if (!filename) {
        alert('Please enter a file name');
        return;
    }

    const jsonData = {
        "filename": filename,
        "PrePrompt": data.get('PrePrompt'),
        "model": data.get('model'),
        "temperature": parseFloat(data.get('temperature')),
        "top_p": parseFloat(data.get('top_p')),
        "n": parseInt(data.get('n')),
        "presence_penalty": parseFloat(data.get('presence_penalty')),
        "frequency_penalty": parseFloat(data.get('frequency_penalty')),
        "max_completion_tokens": parseInt(data.get('max_completion_tokens'))
    };

    fetch('/create-json', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error('Error:', error));
}

function selectAPI(apiName) {
    fetch('/select-api', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ api_name: apiName }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) alert(data.message);
        else if (data.error) alert(data.error);
    })
    .catch(error => console.error('Error:', error));
}

function showForm(formId) {
    const forms = document.querySelectorAll('main');
    forms.forEach(form => form.style.display = 'none');
    document.getElementById(formId).style.display = 'block';
    localStorage.setItem('activeForm', formId);
    const buttons = document.querySelectorAll('.researcher-sidebar-content');
    buttons.forEach(button => button.classList.remove('active-button'));
    document.querySelector(`button[onclick="showForm('${formId}')"]`).classList.add('active-button');
}

async function listJsonFiles() {
    try {
        const response = await fetch('/list-json-files');
        const files = await response.json();
        files.sort();
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';

        files.forEach(filename => {
            const listItem = document.createElement('li');
            listItem.textContent = filename;
            listItem.onmouseover = () => showFileContent(filename);
            listItem.onmouseout = hideFileContent;
            fileList.appendChild(listItem);
        });
    } catch (error) {
        console.error('Error fetching files:', error);
    }
}

async function showFileContent(filename) {
    try {
        const response = await fetch(`/get-file-content?name=${filename}`);
        const content = await response.text();
        const popup = document.getElementById('file-content-popup');
        popup.textContent = content;
        popup.style.display = 'block';
    } catch (error) {
        console.error('Error fetching file content:', error);
    }
}

function hideFileContent() {
    const popup = document.getElementById('file-content-popup');
    popup.style.display = 'none';
}

async function populateAgentDropdown() {
    try {
        const response = await fetch('/list-json-files');
        const conditions = await response.json();
        const select = document.getElementById('agent');
        select.innerHTML = '';

        conditions.forEach(condition => {
            const option = document.createElement('option');
            option.value = condition;
            option.textContent = condition;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching conditions:', error);
    }
}

async function updatePasswords() {
    const password = document.getElementById('password').value;
    const agent = document.getElementById('agent').value.replace('.json', '');
    const response = await fetch('/update-passwords', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ password, agent })
    });

    alert(response.ok ? 'Passwords updated successfully' : 'Failed to update');
}

function sortTableRows() {
    const tableBody = document.getElementById('password-table-body');
    const rows = Array.from(tableBody.rows);
    rows.sort((a, b) => a.cells[0].textContent.localeCompare(b.cells[0].textContent));
    rows.forEach(row => tableBody.appendChild(row));
}

async function listPasswords() {
    try {
        const response = await fetch('/get-passwords');
        const passwords = await response.json();
        const tableBody = document.getElementById('password-table-body');
        tableBody.innerHTML = '';

        for (let item of passwords) {
            const row = document.createElement('tr');
            const filename = `${item.password}.json`;

            try {
                const fileContentResponse = await fetch(`/get-file-content?name=${filename}`);
                const fileContent = fileContentResponse.ok ? await fileContentResponse.text() : 'No content';

                row.innerHTML = `
                    <td>${item.password || 'No password'}</td>
                    <td>${item.agent}</td>
                    <td>${fileContent}</td>
                `;
            } catch (error) {
                console.error('Error fetching file content:', error);
                row.innerHTML = `
                    <td>${item.password || 'No password'}</td>
                    <td>${item.agent}</td>
                    <td>Error loading content</td>
                `;
            }

            tableBody.appendChild(row);
        }
        
        sortTableRows();
    } catch (error) {
        console.error('Error fetching passwords:', error);
    }
}

function downloadFile(filename) {
    window.location.href = `/download/${filename}`;
}

document.getElementById('model').addEventListener('change', function() {
    document.getElementById('custom-model').style.display = this.value === 'custom' ? 'block' : 'none';
  });