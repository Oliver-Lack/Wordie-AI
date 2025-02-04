# run using terminal: python add_passwords.py
# This script is used to initialise a users.db with passwords connected to agent conditions.
# Once this script has been run, using these passwords in login will load their respective agent into wordie.ai.

import sqlite3

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

def add_passwords():
    passwords = {
        'hat': '1_TEMP_high',
        'lake': '1_TEMP_low',
        'music': '1_TEMP_mid',
        'red': '2_TEMP_high',
        'blue': '2_TEMP_low',
        'orange': '2_TEMP_mid',
        'apple': '1_PROMPT_high',
        'dingo': '1_PROMPT_low',
        'swim': '2_PROMPT_high',
        'run': '2_PROMPT_low',
        'pilot1': 'temp0',
        'pilot2': 'temp0_2',
        'pilot3': 'temp0_4',
        'pilot4': 'temp0_7',
        'pilot5': 'temp1',
        'pilot6': 'temp1_2',
        'pilot7': 'temp1_4',
        'pilot8': 'temp1_7',
        'pilot9': 'temp2',
        'wordie123': 'default',
        'elderberry': 'experimental',
        'gpt4o': 'llm_gpt4o',
        'o1': 'llm_o1',
    }

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    for password, agent in passwords.items():
        c.execute('INSERT OR REPLACE INTO passwords (password, agent) VALUES (?, ?)', (password, agent))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    add_passwords()