import sqlite3
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from API import API_Call
import sys
import os
import json
from datetime import datetime
import subprocess
import math
import webview
import csv

# Function to initialize the SQLite database for users, passwords, and chat message history.
def init_db():
    conn = sqlite3.connect('users.db')
    conn.text_factory = str
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 username TEXT NOT NULL UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 message TEXT NOT NULL,
                 response TEXT NOT NULL,
                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (user_id) REFERENCES users (id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS passwords 
                 (password TEXT PRIMARY KEY, 
                 agent TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Initialize the database and wordie instance outside of any function for Gunicorn and AWS integration
init_db()
wordie = API_Call() 

# Run add_passwords.py script to initialise the users.db with passwords connected to agent conditions
subprocess.run([sys.executable, 'add_passwords.py'])

# Create a Flask app instance and set a secret key for session management
app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']

# Function to calculate and return the joint logarithmic probability from logprobs.
    # This function was changed from the exponentiated sum of loprobs to JUST the sum of logprobs.
    # This is because of underflow problems, approximating the former as 0 for most sequences. 
    # This function returns the joint log probability from logprobs.
        # You can compare log probability sums directly. The less negative the value, the 
        # higher the probability. For example, if one log probability is -5 and another is -10, 
        # the former represents a higher probability than the latter.
def calculate_joint_log_probability(logprobs):
    return sum(logprobs) 

# Function to log data to JSON file
def log_user_data(data):
    try:
        with open('interactions.json', 'r') as f:
            file_content = f.read().strip()
            interactions = json.loads(file_content) if file_content else {"users": {}}
    except (FileNotFoundError, json.JSONDecodeError):
        interactions = {"users": {}}

    user_id = str(data['user_id'])
    if user_id not in interactions["users"]:
        interactions["users"][user_id] = {
            "username": data.get('username', ''),
            "interactions": []
        }

    interaction_type = 'message' if 'message' in data else 'action'
    interaction_content = {k: v for k, v in data.items() if k not in ['user_id', 'username']}
    
    # Calculate and add the relativeSequenceJointLogProbability
    logprobs = data.get('logprobs', [])
    interaction_content['relativeSequenceJointLogProbability'] = calculate_joint_log_probability(logprobs)
    
    # Creating variable with all of users logprobs from interaction
    all_logprobs = []
    for interaction in interactions["users"][user_id]["interactions"]:
        if 'logprobs' in interaction:
            all_logprobs.extend(interaction['logprobs'])

    # Include the logprobs from the current message too
    all_logprobs.extend(logprobs)

    #Calculate and add the relativeInteractionJointLogProbability
    interaction_content['relativeInteractionJointLogProbability'] = calculate_joint_log_probability(all_logprobs)
    
    # Add interaction content to user interactions
    interactions["users"][user_id]["interactions"].append(interaction_content)

    # Write updated data back to the JSON file
    with open('interactions.json', 'w') as f:
        json.dump(interactions, f, indent=4)

       # Also append to CSV
    csv_headers = ["timestamp", "user_id", "username", "interaction_type", "message", "response", "model", "temperature", "logprobs"]
    interaction_data = [
        data.get('timestamp', ''),
        data.get('user_id', ''),
        data.get('username', ''),
        interaction_type,
        data.get('message', ''),
        data.get('response', ''),
        data.get('model', ''),
        data.get('temperature', ''),
        logprobs
    ]

    # Check if CSV needs headers
    csv_file = 'interactions_backup.csv'
    write_headers = not os.path.exists(csv_file)

    with open(csv_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_headers:
            writer.writerow(csv_headers)
        writer.writerow(interaction_data)

# Add a new user to the users table
def add_user(username):
    conn = sqlite3.connect('users.db')
    conn.text_factory = str
    c = conn.cursor()
    c.execute('INSERT INTO users (username) VALUES (?)', (username,))
    conn.commit()
    conn.close()

# Add a message and its response to the messages table
def add_message(user_id, message, response, model, temperature, prompt_tokens, completion_tokens, total_tokens, logprobs_list):
    conn = sqlite3.connect('users.db')
    conn.text_factory = str
    c = conn.cursor()
    c.execute('INSERT INTO messages (user_id, message, response) VALUES (?, ?, ?)', 
              (user_id, message, response))
    conn.commit()
    conn.close()
    log_user_data({
        'user_id': user_id,
        'username': session.get('username'),
        'message': message,
        'response': response,
        'model': model,
        'temperature': temperature,
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': total_tokens,
        'logprobs': logprobs_list,  # Log each token's log probability list
        'timestamp': str(datetime.now())
    })

# Get the conversation history for a user
def get_messages(user_id, systemprompt):
    conn = sqlite3.connect('users.db')
    conn.text_factory = str
    conversation = []
    c = conn.cursor()
    c.execute('SELECT * FROM messages WHERE user_id = ? ORDER BY timestamp', (user_id,))
    messages = c.fetchall()
    conversation.append({"role": "system", "content": systemprompt})
    for message in messages:
        conversation.append({"role": "user", "content": message[2]})
        conversation.append({"role": "assistant", "content": message[3]})
    conn.close()
    return conversation

# Define a route for the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        if user:
            user_id = user[0]
        else:
            c.execute('INSERT INTO users (username) VALUES (?)', (username,))
            user_id = c.lastrowid
            conn.commit()
        c.execute('SELECT agent FROM passwords WHERE password = ?', (password,))
        agent = c.fetchone()
        if agent:
            session['user_id'] = user_id
            session['username'] = username
            session['agent'] = agent[0]
            wordie.update_agent(f"agents/{agent[0]}.json")  # Update the agent for the wordie instance
            flash('', 'success')
            conn.close()
            return redirect(url_for('chat'))
        else:
            flash('Invalid password', 'error')
            conn.close()
            return redirect(url_for('login'))
    return render_template('login.html')

# Define a route for the chat page
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    env_var = os.environ.get('OPENAI_API_KEY')
    show_popup = env_var is None

    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        agent = session.get('agent', 'default')
        wordie.update_agent(f"agents/{agent}.json")
        conversation = get_messages(session['user_id'], wordie.agent_data["PrePrompt"])

        if request.method == 'POST':
            message = request.form.get('message')
            if not message:
                flash('Message cannot be empty', 'error')
                return jsonify({'error': 'Message cannot be empty'}), 400
            
            model = wordie.agent_data.get("model", "gpt-4o")
            try:
                conversation, prompt_tokens, completion_tokens, total_tokens, logprobs_list = wordie.thinkAbout(message, conversation, model=model)
                response = conversation[-1]["content"]
                user_id = session['user_id']
                add_message(user_id, message, str(response), model, wordie.agent_data["temperature"], prompt_tokens, completion_tokens, total_tokens, logprobs_list)
                return jsonify({'response': response})
            except Exception as e:
                app.logger.error(f"Error processing message: {e}")
                return jsonify({'error': 'Error processing message'}), 500

        return render_template('chat.html', username=session['username'], messages=conversation, show_popup=show_popup)
    except Exception as ex:
        app.logger.error(f"Unexpected error occurred: {ex}")
        return jsonify({'error': 'Unexpected error occurred'}), 500

# Define a route for the logout functionality
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    log_user_data({
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'action': 'logout',
        'timestamp': str(datetime.now())
    })
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You are being redirected', 'success')
    return redirect(url_for('QUALTRICSredirection.com'))


if __name__ == '__main__':
    # No need to call init_db() or create wordie here, as it's done at the module level for Gunicorn and AWS integration.
    pass