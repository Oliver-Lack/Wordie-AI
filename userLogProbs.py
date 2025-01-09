# Similar to logProbs.py, except for calculating the joint probability of user messages and interactions. 

### ....Figure out a way to go backwards from this and calculate the humans temperature based on comparison to tempConditions joint probability. 


import openai
import json
import os

# Make sure you have the API key set up
openai.api_key = os.getenv("OPENAI_API_KEY")

def calculate_logprobs_for_message(message, model="gpt-3.5-turbo"):
    # Prepare the tokenized message
    tokens = [token for token in message.split()]
    previous_tokens = []

    logprobs = []
    
    for i, token in enumerate(tokens):
        # Prepare the input with previous tokens
        prompt = ' '.join(previous_tokens)
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=1,
            temperature=0,  # zero temperature gives you deterministic results for logprobs
            logprobs=1,
            echo=True
        )

        # Extract logprob for the current token
        token_logprob = None
        for choice in response.choices:
            logprobs_data = choice.logprobs
            if 'tokens' in logprobs_data:
                token_index = logprobs_data['tokens'].index(token)
                token_logprob = logprobs_data['token_logprobs'][token_index]

        if token_logprob is not None:
            logprobs.append(token_logprob)

        # Add current token to previous tokens
        previous_tokens.append(token)
    
    return logprobs

def process_interactions_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    # Iterate over each user and their interactions
    for user_id, user_data in data['users'].items():
        for interaction in user_data['interactions']:
            if interaction['type'] == 'message':
                message = interaction['content']['message']
                # Calculate logprobs for this message
                logprobs = calculate_logprobs_for_message(message)
                # Add the logprobs to the interaction content
                interaction['content']['user_logprobs'] = logprobs

    # Save the modified JSON back to the file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Usage Example
process_interactions_file('interactions.JSON')