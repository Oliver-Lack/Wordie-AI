import sqlite3
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from API import API_Call
import sys
import os
import json
from datetime import datetime
import subprocess
import csv
import boto3

# Batch for S3 AWS bucket backup
interaction_batch = []

# Setup with boto3 aws CLI for S3 AWS bucket backup to dump the batched interactions
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
sts_client = boto3.client('sts')
response = sts_client.assume_role(
    RoleArn='arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME',
    RoleSessionName='session_name'
)
credentials = response['Credentials']

s3 = boto3.client(
    's3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken']
)


# database initialization for usernames, passwords, and conversation history
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
                 password TEXT NOT NULL,
                 message TEXT NOT NULL,
                 response TEXT NOT NULL,
                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (user_id) REFERENCES users (id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS passwords 
                 (password TEXT PRIMARY KEY, 
                 agent TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()
wordie = API_Call()

# Adding conditions to the passwords
subprocess.run([sys.executable, 'add_passwords.py'])

# Initializing the flask app
app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']

def calculate_joint_log_probability(logprobs):
    return sum(logprobs)
# For logging interactions.json, interactions_backup.csv, and batched_interactions.json
def log_user_data(data):
    global interaction_batch

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

    interaction_content = {k: v for k, v in data.items() if k not in ['user_id', 'username']}
    interaction_content['password'] = session.get('password', 'N/A')

    if 'logprobs' in data:
        logprobs = data.get('logprobs', [])
        interaction_content['relativeSequenceJointLogProbability'] = calculate_joint_log_probability(logprobs)
        all_logprobs = [lp for interaction in interactions["users"][user_id]["interactions"] if 'logprobs' in interaction for lp in interaction['logprobs']]
        all_logprobs.extend(logprobs)
        interaction_content['relativeInteractionJointLogProbability'] = calculate_joint_log_probability(all_logprobs)

    interactions["users"][user_id]["interactions"].append(interaction_content)

    with open('interactions.json', 'w') as f:
        json.dump(interactions, f, indent=4)

    csv_headers = [
        "timestamp", "user_id", "username", "password", "interaction_type", 
        "message", "response", "model", "temperature", "logprobs"
    ]
    interaction_data = [
        data.get('timestamp', ''),
        data.get('user_id', ''),
        data.get('username', ''),
        session.get('password', 'N/A'),
        data.get('interaction_type', ''),
        data.get('message', ''),
        data.get('response', ''),
        data.get('model', ''),
        data.get('temperature', ''),
        data.get('logprobs', [])
    ]

    csv_file = 'interactions_backup.csv'
    write_headers = not os.path.exists(csv_file)

    with open(csv_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_headers:
            writer.writerow(csv_headers)
        writer.writerow(interaction_data)

    interaction_batch.append(data)

    if len(interaction_batch) >= 20:
        process_and_store_batch(interaction_batch)
        interaction_batch.clear()
# Upload function for AWS S3 backup data dump
def upload_to_s3(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    s3.upload_file(file_name, bucket, object_name)
# Batching data for S3 AWS bucket backup
def process_and_store_batch(batch):
    batch_json = json.dumps(batch, indent=4)
    with open('batched_interactions.json', 'a') as f:
        f.write(batch_json + '\n')
    upload_to_s3('batched_interactions.json', S3_BUCKET_NAME)

def add_user(username):
    conn = sqlite3.connect('users.db')
    conn.text_factory = str
    c = conn.cursor()
    c.execute('INSERT INTO users (username) VALUES (?)', (username,))
    conn.commit()
    conn.close()

def add_message(user_id, password, message, response, model, temperature, prompt_tokens, completion_tokens, total_tokens, logprobs_list):
    conn = sqlite3.connect('users.db')
    conn.text_factory = str
    c = conn.cursor()
    c.execute('INSERT INTO messages (user_id, password, message, response) VALUES (?, ?, ?, ?)', 
              (user_id, password, message, response))
    conn.commit()
    conn.close()
    log_user_data({
        'user_id': user_id,
        'username': session.get('username'),
        'interaction_type': 'message',
        'message': message,
        'response': response,
        'model': model,
        'temperature': temperature,
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': total_tokens,
        'logprobs': logprobs_list,
        'timestamp': str(datetime.now())
    })

def get_messages(user_id, password, systemprompt):
    conn = sqlite3.connect('users.db')
    conn.text_factory = str
    conversation = []
    c = conn.cursor()
    c.execute('SELECT * FROM messages WHERE user_id = ? AND password = ? ORDER BY timestamp', (user_id, password))
    messages = c.fetchall()
    conversation.append({"role": "system", "content": systemprompt})
    for message in messages:
        conversation.append({"role": "user", "content": message[3]})
        conversation.append({"role": "assistant", "content": message[4]})
    conn.close()
    return conversation

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
            session['password'] = password
            session['agent'] = agent[0]
            wordie.update_agent(f"agents/{agent[0]}.json")
            flash('', 'success')
            conn.close()
            return redirect(url_for('chat'))
        else:
            flash('Invalid password', 'error')
            conn.close()
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    env_var = os.environ.get('OPENAI_API_KEY')
    show_popup = env_var is None

    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        agent = session.get('agent', 'default')
        wordie.update_agent(f"agents/{agent}.json")
        conversation = get_messages(session['user_id'], session['password'], wordie.agent_data["PrePrompt"])

        if request.method == 'POST':
            message = request.form.get('message')
            if not message:
                flash('Message cannot be empty', 'error')
                return jsonify({'error': 'Message cannot be empty'}), 400
            
            model = wordie.agent_data.get("model", "gpt-4o")
            try:
                conversation, prompt_tokens, completion_tokens, total_tokens, logprobs_list = wordie.thinkAbout(message, conversation, model=model)
                response = conversation[-1]["content"]
            except Exception as e:
                app.logger.error(f"Error processing message: {e}")
                return jsonify({'error': 'Error processing message'}), 500

            user_id = session['user_id']
            password = session['password']
            add_message(user_id, password, message, str(response), model, wordie.agent_data["temperature"], prompt_tokens, completion_tokens, total_tokens, logprobs_list)
            return jsonify({'response': response})

        return render_template('chat.html', username=session['username'], messages=conversation, show_popup=show_popup)
    except Exception as ex:
        app.logger.error(f"Unexpected error occurred: {ex}")
        return jsonify({'error': 'Unexpected error occurred'}), 500

if __name__ == '__main__':
    pass