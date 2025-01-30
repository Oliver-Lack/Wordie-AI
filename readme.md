# Wordie is a Flask based AI interface web app for Human-AI interaction research

The app runs with gunicorn for the production server, currently integrated with an OpenAI API, and dumps data to various files when API calls are made. This includes interactions.json, interactions_backup.csv, and AWS S3 bucket API integration. 
Each data files collects the same data from the interaction. Namely:
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


## How to run Wordie locally:

1. Setup environment variables

- Register for an LLM API key and and create an environment variable named "OPENAI_API_KEY" with the key in it
- Create an env variable named "FLASK_SECRET_KEY" with a secret key for the Flask app
- For AWS S3 bucket integration on a production server, follow AWS documentation (S3 not necessary for local development, currently just a backup data dump method) 

Here's a rough bash command to set the env variables when deploying an EC2 instance:
            #!/bin/bash
            # OpenAI API Key
            export OPENAI_API_KEY="your-openai-api-key"

            # Flask Secret Key
            export FLASK_SECRET_KEY="your-flask-secret-key"

            # AWS Credentials
            export AWS_ACCESS_KEY_ID="your-aws-access-key-id"
            export AWS_SECRET_ACCESS_KEY="your-aws-secret-access-key"
            export AWS_DEFAULT_REGION="your-aws-region"

            echo "Environment variables have been set."


4. Start the app

To start Wordie, run the following command:

```
gunicorn -w 4 -b 0.0.0.0:8000 wordie:app

```

5. Upon starting the app, you will be prompted to login with a prolific ID and password that is connected to an agent (experimental condition). 


## How to run Wordie on an AWS EC2 Instance (on a magical cloud connected to this thing called the internet):


Got to README_EC2_Setup.md for a step by step guide on how to deploy Wordie on an AWS EC2 instance.



## Latest Experiment NOTES

For other researchers:
- The app currently logs data to my S3 bucket on AWS. Change the details in the wordie.py and setup your own bucket. 

Extra info:
- If the agents are edited, the app needs to be reset to apply the changes.
- o1 model and agent will not work as the API is not yet available (released on 17/12/24)
- Numbers labelling agent conditions 1 = AI is guesser 2 = AI is giver.

ToDo:
- Connect conversation history to username AND password. 
- S3 Bucket send data 
- Get other models working

Measures of unpredictability required:
1. joint probability of sequence and interactions (iterated exponent of the summed logprobs)
2. prompt engineering score
3. Human Perception of unpredictability (survey)
4. zipf law score