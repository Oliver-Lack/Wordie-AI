# Wordie is a Flask based AI interface web app for Human-AI interaction research

The app runs with gunicorn, currently integrated with an OpenAI API, and dumps data to various files when API calls are made. This includes interactions.json, interactions_backup.csv, and AWS S3 bucket API integration. 
Each data files collects the same data from the interaction. That is:
- user_id
- prolific_id
- temperature
- model
- user message
- AI message
- logprobs (log probabilities) of AI message
- sequence log probability
- interaction log probability
- prompt-tokens
- completion-tokens
- total-tokens
- timestamps

The users.db is used to store prolific IDs, interface assigned user_ids, conversation history, and passwords for experimental condition assignment.
The users.db is used for the apps functionality and not data collection or analyses. 


## How to run Wordie:

1. Register for an API key and and create an environment variable named "OPENAI_API_KEY" with the key in it

2. Start the app

To start Wordie, run the following command:

```
gunicorn -w 4 -b 0.0.0.0:8000 wordie:app

```

3. Upon starting the app, you will be prompted to login with a prolific ID and password that is connected to an agent (experimental condition). 



Extra info:

- If the agents are edited, the app needs to be reset to apply the changes.
- o1 model and agent will not work as the API is not yet available (released on 17/12/24)
- Numbers labelling agent conditions 1 = AI is guesser 2 = AI is giver.


ToDo:
8. S3 Bucket send data 
9. Get other models working

Measures of unpredictability required:
1. joint probability of sequence and interactions (iterated exponent of the summed logprobs)
2. prompt engineering score
3. Human Perception of unpredictability (survey)
4. zipf law score