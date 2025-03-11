import os
import json

def update_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)

            data['max_completion_tokens'] = 300  # Ensure it's set to 300
            
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)

agents_directory = 'agents'
update_json_files(agents_directory)